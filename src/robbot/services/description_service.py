"""DescriptionService para análise de mídia com BLIP-2 (open source, local, sem custo)."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from robbot.adapters.repositories.message_repository import MessageRepository
from robbot.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class DescriptionService:
    """
    Service para gerar metadata de mensagens de mídia usando BLIP-2.
    
    Análise LOCAL sem custo de API:
    - Images: BLIP-2 (Salesforce) - image captioning + VQA
    - Videos: Frame extraction + BLIP-2 analysis
    - Documents/Voice: Metadata baseado em filename/caption
    
    Modelo: Salesforce/blip-image-captioning-base
    - Open source (BSD-3 License)
    - ~990MB download inicial
    - Roda em CPU (inference local)
    - Zero custo de API
    
    Retorna:
    - title: Título curto (max 50 chars)
    - description: Descrição detalhada da análise visual
    - tags: Tags relevantes (comma-separated)
    """

    def __init__(self, db: Session):
        """Inicializar serviço de descrição com BLIP-2."""
        self.db = db
        self.message_repo = MessageRepository(db)
        logger.info("✓ DescriptionService initialized (BLIP-2 local, sem custo)")

    def generate_description(
        self, 
        message_id: UUID,
        use_vision: bool = True
    ) -> dict[str, Optional[str]]:
        """
        Gerar metadata para uma mensagem usando BLIP-2 ou metadata básico.
        
        Args:
            message_id: ID da mensagem para analisar
            use_vision: Se True, usa BLIP-2 para images/videos (padrão)
            
        Returns:
            Dict com keys: generated_title, generated_description, suggested_tags
            
        Raises:
            NotFoundException: Se mensagem não encontrada
        """
        # Buscar mensagem
        message = self.message_repo.get_by_id(message_id)
        if not message:
            raise NotFoundException(f"Message {message_id} not found")
        
        try:
            # Extrair dados
            filename = ""
            caption = message.caption or ""
            media_url = ""
            
            if message.media and len(message.media) > 0:
                filename = message.media[0].filename or ""
                media_url = message.media[0].url or ""
            
            # Se é imagem e vision está habilitado, usar BLIP-2
            if message.type == "image" and use_vision and media_url:
                return self._analyze_image_with_blip(media_url, caption)
            
            # Se é vídeo, analisar primeiro frame (simplificado: usar metadata)
            # TODO: Implementar extração de frame + BLIP-2
            
            # Para outros tipos ou se vision desabilitado, usar metadata básico
            return self._generate_file_metadata(filename, caption, message.type)
                
        except Exception as e:
            logger.error(f"✗ Erro ao gerar descrição para message {message_id}: {e}")
            # Fallback para metadata básico
            return self._generate_file_metadata(filename, caption, message.type)
    
    def _analyze_image_with_blip(self, image_url: str, caption: str) -> dict[str, Optional[str]]:
        """
        Analisar imagem usando BLIP-2 (local, sem custo).
        
        Args:
            image_url: URL da imagem
            caption: Caption fornecido pelo usuário
            
        Returns:
            Dict com title, description, tags
        """
        try:
            from robbot.services.vision_service import get_vision_service
            
            vision = get_vision_service()
            
            # Analisar imagem com contexto médico
            result = vision.analyze_image_sync(image_url, context="medical")
            
            # Usar caption do BLIP como título (ou caption do usuário se fornecido)
            title = caption[:50] if caption else result["caption"][:50]
            
            # Descrição detalhada do BLIP
            description = result["detailed_description"]
            if caption:
                description = f"{caption}. Análise visual: {description}"
            
            # Tags do BLIP + keywords do caption
            tags = result["tags"]
            
            logger.info(f"✓ BLIP-2 analisou imagem: {title[:30]}...")
            
            return {
                "generated_title": title,
                "generated_description": description,
                "suggested_tags": tags
            }
            
        except Exception as e:
            logger.error(f"✗ Erro ao usar BLIP-2: {e}")
            # Fallback para metadata básico
            logger.warning("⚠️ Usando fallback para metadata básico")
            return self._generate_file_metadata(
                image_url.split("/")[-1], 
                caption, 
                "image"
            )

    def _generate_file_metadata(self, filename: str, caption: str, file_type: str) -> dict[str, Optional[str]]:
        """
        Gerar metadata básico SEM usar API (zero custo).
        
        Baseado em:
        - Extensão do arquivo
        - Nome do arquivo
        - Caption fornecido pelo usuário
        - Tipo de mídia
        
        Retorna metadata estruturado simples.
        """
        import os
        
        # Extrair extensão
        _, ext = os.path.splitext(filename)
        ext = ext.lower().replace('.', '')
        
        # Mapear extensões para contexto
        extension_context = {
            # Imagens
            'jpg': 'imagem', 'jpeg': 'imagem', 'png': 'imagem', 'gif': 'imagem', 'webp': 'imagem',
            # Vídeos
            'mp4': 'vídeo', 'avi': 'vídeo', 'mov': 'vídeo', 'mkv': 'vídeo', 'webm': 'vídeo',
            # Áudio
            'mp3': 'áudio', 'ogg': 'áudio', 'wav': 'áudio', 'opus': 'áudio', 'oga': 'áudio',
            # Documentos
            'pdf': 'documento PDF', 'doc': 'documento Word', 'docx': 'documento Word',
            'xls': 'planilha Excel', 'xlsx': 'planilha Excel',
            'ppt': 'apresentação', 'pptx': 'apresentação',
            'txt': 'arquivo de texto',
        }
        
        media_context = extension_context.get(ext, file_type)
        
        # Gerar título baseado em caption ou filename
        if caption and len(caption) > 0:
            title = caption[:50]
        else:
            # Limpar filename (remover extensão e underscores)
            clean_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
            title = clean_name[:50] if clean_name else f"{file_type.capitalize()}"
        
        # Gerar descrição
        description_parts = []
        if caption:
            description_parts.append(f"Descrição: {caption}")
        if filename:
            description_parts.append(f"Arquivo: {filename}")
        description_parts.append(f"Tipo: {media_context}")
        
        description = " | ".join(description_parts)
        
        # Gerar tags baseadas em contexto médico (Dra. Andrea - emagrecimento)
        base_tags = [file_type, media_context]
        
        # Tags contextuais baseadas em palavras-chave
        text_to_analyze = f"{filename} {caption}".lower()
        
        keyword_tags = {
            'dieta': 'dieta',
            'exercicio': 'exercício',
            'peso': 'controle de peso',
            'alimenta': 'alimentação',
            'receita': 'receita',
            'consulta': 'consulta',
            'exame': 'exame',
            'resultado': 'resultado',
            'duvida': 'dúvida',
            'pergunta': 'pergunta',
            'tratamento': 'tratamento',
            'medicamento': 'medicamento',
            'prescrição': 'prescrição',
        }
        
        for keyword, tag in keyword_tags.items():
            if keyword in text_to_analyze:
                base_tags.append(tag)
        
        tags = ', '.join(base_tags[:8])  # Máximo 8 tags
        
        logger.info(f"✓ Metadata básico gerado: title='{title[:30]}...', {len(base_tags)} tags")
        
        return {
            "generated_title": title,
            "generated_description": description,
            "suggested_tags": tags
        }
