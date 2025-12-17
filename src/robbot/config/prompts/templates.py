"""
Sistema de prompts para Gemini AI.

Este módulo centraliza todos os prompts usados no sistema,
permitindo versionamento e fácil manutenção.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PromptTemplates:
    """
    Templates de prompts para diferentes casos de uso.
    
    Responsabilidades:
    - Fornecer prompts padronizados
    - Permitir personalização com variáveis
    - Versionar prompts
    """
    
    VERSION = "1.0.0"
    
    # ========== PROMPT BASE ==========
    BASE_SYSTEM_PROMPT = """Você é um assistente virtual inteligente de uma empresa de vendas.

INSTRUÇÕES GERAIS:
- Seja educado, profissional e prestativo
- Responda em português do Brasil
- Mantenha respostas objetivas (máximo 3 parágrafos)
- Use informações do contexto quando disponível
- Se não souber algo, seja honesto e ofereça ajuda alternativa
- Não invente informações ou preços

CONTEXTO DA CONVERSA:
{context}

HISTÓRICO:
{history}
"""

    # ========== DETECÇÃO DE INTENÇÃO ==========
    INTENT_DETECTION_PROMPT = """Analise a mensagem do usuário e identifique a INTENÇÃO principal.

MENSAGEM: "{message}"

CONTEXTO ANTERIOR:
{context}

INTENÇÕES POSSÍVEIS:
1. INTERESSE_PRODUTO - Cliente interessado em produtos/serviços
2. DUVIDA_TECNICA - Dúvidas sobre funcionamento/especificações
3. ORCAMENTO - Solicitação de orçamento/preço
4. AGENDAMENTO - Deseja agendar reunião/visita
5. RECLAMACAO - Problema ou insatisfação
6. INFORMACAO - Busca informações gerais
7. SAUDACAO - Cumprimento inicial
8. DESPEDIDA - Finalização da conversa
9. CONFIRMACAO - Confirmar interesse/compra
10. OUTRO - Não se encaixa nas anteriores

Responda APENAS com o nome da intenção (ex: INTERESSE_PRODUTO).
"""

    # ========== SCORING DE MATURIDADE ==========
    MATURITY_SCORING_PROMPT = """Avalie o nível de MATURIDADE DO LEAD baseado na conversa.

CONVERSA ATUAL:
{conversation_text}

HISTÓRICO DE INTERAÇÕES:
{interaction_history}

CRITÉRIOS DE AVALIAÇÃO:
1. Engajamento (0-25 pontos)
   - Frequência de respostas
   - Qualidade das perguntas
   - Tempo de resposta

2. Interesse (0-25 pontos)
   - Demonstra necessidade clara
   - Fez perguntas específicas
   - Mencionou orçamento/timeline

3. Qualificação (0-25 pontos)
   - Tem poder de decisão
   - Tem budget
   - Timeline definido

4. Prontidão (0-25 pontos)
   - Urgência demonstrada
   - Próximos passos claros
   - Sinais de fechamento

SCORE ATUAL: {current_score}

Analise a conversa e responda em JSON:
{{
    "score": <0-100>,
    "reasoning": "<breve explicação>",
    "next_action": "<recomendação>"
}}
"""

    # ========== GERAÇÃO DE RESPOSTA ==========
    RESPONSE_GENERATION_PROMPT = """Gere uma resposta adequada para o cliente.

MENSAGEM DO CLIENTE: "{user_message}"

INTENÇÃO DETECTADA: {intent}

CONTEXTO RELEVANTE:
{context}

INFORMAÇÕES DO LEAD:
- Score de Maturidade: {maturity_score}/100
- Status: {lead_status}
- Última Interação: {last_interaction}

INSTRUÇÕES ESPECÍFICAS:
- Responda de forma natural e conversacional
- Seja proativo sugerindo próximos passos
- Se score > 70, seja mais direto sobre fechamento
- Se score < 40, foque em educar e qualificar
- Mencione informações do contexto quando relevante

Gere APENAS a resposta (sem meta-informações).
"""

    # ========== EXTRAÇÃO DE CONTEXTO ==========
    CONTEXT_EXTRACTION_PROMPT = """Extraia informações-chave da mensagem para contexto.

MENSAGEM: "{message}"

EXTRAIA (quando presente):
- Produtos/serviços mencionados
- Valores/orçamento mencionados
- Datas/prazos mencionados
- Preferências do cliente
- Objeções ou preocupações
- Decisores envolvidos

Responda em JSON:
{{
    "products": ["produto1", "produto2"],
    "budget": "<valor ou null>",
    "timeline": "<prazo ou null>",
    "preferences": ["pref1", "pref2"],
    "objections": ["obj1"],
    "decision_makers": ["pessoa1"]
}}
"""

    # ========== FALLBACK ==========
    FALLBACK_PROMPT = """Gere uma resposta de fallback apropriada.

SITUAÇÃO: {situation}
ÚLTIMO ERRO: {error}

INSTRUÇÕES:
- Seja educado e mostre que está tentando ajudar
- Ofereça alternativas (falar com humano, tentar reformular)
- Não exponha detalhes técnicos do erro
- Mantenha tom profissional

Gere resposta de fallback.
"""

    @classmethod
    def format_base_prompt(
        cls,
        context: str = "",
        history: str = ""
    ) -> str:
        """
        Formatar prompt base com contexto e histórico.
        
        Args:
            context: Contexto relevante da conversa
            history: Histórico de mensagens
            
        Returns:
            Prompt formatado
        """
        return cls.BASE_SYSTEM_PROMPT.format(
            context=context or "[Nenhum contexto disponível]",
            history=history or "[Primeira interação]"
        )

    @classmethod
    def format_intent_prompt(cls, message: str, context: str = "") -> str:
        """
        Formatar prompt de detecção de intenção.
        
        Args:
            message: Mensagem do usuário
            context: Contexto anterior
            
        Returns:
            Prompt formatado
        """
        return cls.INTENT_DETECTION_PROMPT.format(
            message=message,
            context=context or "[Sem contexto anterior]"
        )

    @classmethod
    def format_maturity_prompt(
        cls,
        conversation_text: str,
        interaction_history: str = "",
        current_score: int = 0
    ) -> str:
        """
        Formatar prompt de scoring de maturidade.
        
        Args:
            conversation_text: Texto da conversa atual
            interaction_history: Histórico de interações
            current_score: Score atual do lead
            
        Returns:
            Prompt formatado
        """
        return cls.MATURITY_SCORING_PROMPT.format(
            conversation_text=conversation_text,
            interaction_history=interaction_history or "[Primeira conversa]",
            current_score=current_score
        )

    @classmethod
    def format_response_prompt(
        cls,
        user_message: str,
        intent: str,
        context: str = "",
        maturity_score: int = 0,
        lead_status: str = "NEW",
        last_interaction: str = "Agora"
    ) -> str:
        """
        Formatar prompt de geração de resposta.
        
        Args:
            user_message: Mensagem do usuário
            intent: Intenção detectada
            context: Contexto relevante
            maturity_score: Score de maturidade
            lead_status: Status do lead
            last_interaction: Última interação
            
        Returns:
            Prompt formatado
        """
        return cls.RESPONSE_GENERATION_PROMPT.format(
            user_message=user_message,
            intent=intent,
            context=context or "[Sem contexto]",
            maturity_score=maturity_score,
            lead_status=lead_status,
            last_interaction=last_interaction
        )

    @classmethod
    def format_context_extraction_prompt(cls, message: str) -> str:
        """
        Formatar prompt de extração de contexto.
        
        Args:
            message: Mensagem para extrair contexto
            
        Returns:
            Prompt formatado
        """
        return cls.CONTEXT_EXTRACTION_PROMPT.format(message=message)

    @classmethod
    def format_fallback_prompt(cls, situation: str, error: str = "") -> str:
        """
        Formatar prompt de fallback.
        
        Args:
            situation: Descrição da situação
            error: Erro ocorrido (opcional)
            
        Returns:
            Prompt formatado
        """
        return cls.FALLBACK_PROMPT.format(
            situation=situation,
            error=error or "Não especificado"
        )

    @classmethod
    def get_version(cls) -> str:
        """Obter versão dos prompts."""
        return cls.VERSION


# Singleton global
_prompt_templates: Optional[PromptTemplates] = None


def get_prompt_templates() -> PromptTemplates:
    """
    Obter instância singleton de PromptTemplates.
    
    Returns:
        PromptTemplates singleton
    """
    global _prompt_templates
    
    if _prompt_templates is None:
        _prompt_templates = PromptTemplates()
        logger.info(f"🎯 PromptTemplates inicializado (version={PromptTemplates.VERSION})")
    
    return _prompt_templates
