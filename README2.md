# SISTEMA DE ATENDIMENTO CLÍNICA GO

## OBJETIVO PRINCIPAL
<p style="margin-left: 20px;">
Criar um sistema de atendimento automático via WhatsApp que converta pessoas interessadas das campanhas publicitárias em agendamentos de consulta, organizando o fluxo de conversas e transferindo para a secretária quando necessário.
</p>

## O QUE O SISTEMA FAZ

### CAPTAÇÃO E ORGANIZAÇÃO
<div style="margin-left: 20px;">
<ul>
  <li>Recebe mensagens de pessoas que clicam nos anúncios do Google e Instagram</li>
  <li>Organiza as conversas em fila para não se perderem quando chegam muitas ao mesmo tempo</li>
  <li>Identifica de qual campanha cada pessoa veio</li>
  <li>Armazena todas as informações dos interessados</li>
</ul>
</div>

### ATENDIMENTO AUTOMÁTICO INTELIGENTE
<div style="margin-left: 20px;">
<ul>
  <li>Responde automaticamente às perguntas mais comuns</li>
  <li>Mantém o contexto da conversa, lembrando do que já foi falado</li>
  <li>Usa scripts pré-aprovados para garantir que as informações são corretas</li>
  <li>Segue um fluxo de conversa natural, como um atendente humano</li>
</ul>
</div>

### GESTÃO HUMANA
<div style="margin-left: 20px;">
<ul>
  <li>Identifica quando a pessoa quer agendar uma consulta</li>
  <li>Transfere automaticamente para a secretária nesses casos</li>
  <li>Fornece todo o histórico da conversa para a secretária continuar de onde parou</li>
  <li>Mantém a secretária focada apenas no que realmente precisa de intervenção humana</li>
</ul>
</div>

### ACOMPANHAMENTO E MELHORIA
<div style="margin-left: 20px%;">
<ul>
  <li>Mostra em tempo real quantas pessoas estão sendo atendidas</li>
  <li>Mede o tempo de resposta e a eficiência do atendimento</li>
  <li>Acompanha quantas conversas viram agendamentos</li>
  <li>Identifica oportunidades de melhorar os scripts e fluxos</li>
</ul>
</div>

## O QUE O SISTEMA NÃO FAZ
<div style="margin-left: 20px;">
<ul>
  <li>Não substitui completamente a secretária</li>
  <li>Não faz diagnósticos médicos</li>
  <li>Não integra com outras redes sociais além do WhatsApp</li>
  <li>Não envia lembretes automáticos de consultas</li>
</ul>
</div>

## BENEFÍCIOS ESPERADOS

### PARA OS INTERESSADOS
<div style="margin-left: 20px;">
<ul>
  <li>Resposta imediata a qualquer hora</li>
  <li>Atendimento personalizado e contextual</li>
  <li>Não precisar repetir informações</li>
  <li>Agilidade no agendamento</li>
</ul>
</div>

### PARA A CLÍNICA
<div style="margin-left: 20px;">
<ul>
  <li>Atendimento simultâneo a múltiplas pessoas</li>
  <li>Redução de carga de trabalho da secretária</li>
  <li>Aumento de conversão para agendamentos</li>
  <li>Controle total sobre todas as conversas</li>
  <li>Métricas claras do retorno das campanhas</li>
</ul>
</div>

## COMO FUNCIONA NA PRÁTICA
<div style="margin-left: 20px;">
<ol>
  <li>Pessoa vê anúncio e clica para falar no WhatsApp</li>
  <li>Sistema identifica a campanha e inicia o atendimento</li>
  <li>Conversa automática responde dúvidas e qualifica o interesse</li>
  <li>Quando pronto para agendar, transfere para secretária</li>
  <li>Secretária finaliza o agendamento com todas informações</li>
  <li>Sistema registra a conversão e gera relatórios</li>
</ol>

# USER STORIES E FLUXOS DO PROJETO

## USER STORIES PRINCIPAIS

### 1. Como Lead (Pessoa Interessada)
"Quero obter informações sobre procedimentos estéticos da Clínica GO de forma rápida e natural via WhatsApp, e agendar uma consulta quando estiver pronto."

### 2. Como Secretária da Clínica
"Quero gerenciar múltiplas conversas simultaneamente, recebendo apenas os leads prontos para agendamento, com todo o histórico da conversa disponível."

### 3. Como Gestor da Clínica
"Quero acompanhar em tempo real a performance das campanhas ADS, taxas de conversão e eficiência do atendimento automatizado."

### 4. Como Administrador do Sistema
"Quero configurar e ajustar scripts de atendimento, conteúdos multimídia e regras de negócio sem necessidade de intervenção técnica."

---

# FLUXOS DETALHADOS POR USER STORY

## FLUXO 1: Lead Obtém Informações e Agenda
```mermaid
journey
    title Fluxo do Lead: Informação → Agendamento
    section Lead vê anúncio
      Clique no anúncio: 5: Lead
      Abre WhatsApp com mensagem pré-configurada: 5: Lead
    section Interação com Bot
      Recebe saudação contextual: 4: Sistema
      Faz perguntas sobre procedimentos: 5: Lead
      Recebe respostas + mídias explicativas: 4: Sistema
      Expressa interesse em agendar: 5: Lead
    section Finalização com Secretária
      É transferido para atendimento humano: 4: Sistema
      Fornece disponibilidade: 5: Lead
      Confirma agendamento: 5: Lead
      Recebe confirmação: 4: Sistema
FLUXO 2: Secretária Gerencia Conversas
mermaid
Copiar código
journey
    title Fluxo da Secretária: Gestão Eficiente
    section Monitoramento
      Acessa dashboard de conversas: 5: Secretária
      Visualiza conversas ativas e pendentes: 4: Sistema
    section Atendimento Direcionado
      Recebe apenas leads prontos para agendar: 5: Secretária
      Acessa histórico completo da conversa: 4: Sistema
      Continua de onde o bot parou: 5: Secretária
    section Agendamento
      Consulta disponibilidade: 4: Sistema
      Confirma dados do lead: 5: Secretária
      Finaliza agendamento: 5: Secretária
      Sistema registra conversão: 4: Sistema
FLUXO 3: Gestor Monitora Performance
mermaid
Copiar código
journey
    title Fluxo do Gestor: Análise de Resultados
    section Métricas em Tempo Real
      Acessa dashboard de métricas: 5: Gestor
      Visualiza leads por campanha: 4: Sistema
      Monitora taxa de conversão: 4: Sistema
    section Análise de Eficiência
      Avalia tempo médio de resposta: 4: Sistema
      Analisa gargalos no funil: 4: Sistema
      Compara performance entre campanhas: 4: Sistema
    section Tomada de Decisão
      Identifica campanhas mais eficientes: 5: Gestor
      Ajusta orçamento de ADS: 5: Gestor
      Solicita ajustes nos scripts: 5: Gestor
FLUXO 4: Administrador Configura Sistema
mermaid
Copiar código
journey
    title Fluxo do Administrador: Configuração
    section Gestão de Conteúdo
      Acessa painel de scripts: 5: Admin
      Cria/edita scripts por campanha: 5: Admin
      Faz upload de mídias (áudios/vídeos): 5: Admin
    section Configuração de Regras
      Define gatilhos para escalonamento: 5: Admin
      Configura palavras-chave por script: 5: Admin
      Ajusta fluxos conversacionais: 5: Admin
      Monitora saúde do sistema: 4: Sistema
      Ajusta parâmetros de performance: 5: Admin
      Gera backups de configuração: 5: Admin