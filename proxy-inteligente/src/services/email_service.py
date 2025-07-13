import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """Serviço para envio de emails de alerta"""
    
    def __init__(self):
        # Configurações SMTP
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@iasolaris.com.br')
        self.from_name = os.getenv('FROM_NAME', 'IA SOLARIS')
        
        # Email para compra de créditos
        self.credits_email = os.getenv('CREDITS_EMAIL', 'creditos@iasolaris.com.br')
        
        # Configurações de desenvolvimento
        self.debug_mode = os.getenv('EMAIL_DEBUG', 'false').lower() == 'true'
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Envia email genérico"""
        try:
            if self.debug_mode:
                logger.info(f"[DEBUG] Email para {to_email}: {subject}")
                logger.info(f"[DEBUG] Conteúdo: {html_content}")
                return True
            
            if not self.smtp_username or not self.smtp_password:
                logger.warning("Credenciais SMTP não configuradas, simulando envio")
                return True
            
            # Cria mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Adiciona conteúdo texto
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Adiciona conteúdo HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Conecta e envia
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {str(e)}")
            return False
    
    def send_alert_80_percent(self, user) -> bool:
        """Envia alerta de 80% de consumo"""
        subject = "⚠️ Alerta de Consumo - IA SOLARIS"
        
        html_content = self._get_alert_80_template(user)
        text_content = self._get_alert_80_text(user)
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_alert_95_percent(self, user) -> bool:
        """Envia alerta de 95% de consumo"""
        subject = "🚨 URGENTE: Tokens Quase Esgotados - IA SOLARIS"
        
        html_content = self._get_alert_95_template(user)
        text_content = self._get_alert_95_text(user)
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_alert_blocked(self, user) -> bool:
        """Envia alerta de conta bloqueada"""
        subject = "🚫 Conta Bloqueada - Tokens Esgotados - IA SOLARIS"
        
        html_content = self._get_alert_blocked_template(user)
        text_content = self._get_alert_blocked_text(user)
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_credits_purchased_confirmation(self, user, tokens_added: int, transaction_id: str) -> bool:
        """Envia confirmação de compra de créditos"""
        subject = "✅ Créditos Adicionados - IA SOLARIS"
        
        html_content = self._get_credits_confirmation_template(user, tokens_added, transaction_id)
        text_content = self._get_credits_confirmation_text(user, tokens_added, transaction_id)
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def _get_alert_80_template(self, user) -> str:
        """Template HTML para alerta de 80%"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
                .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Alerta de Consumo</h1>
                    <h2>IA SOLARIS</h2>
                </div>
                
                <p>Olá <strong>{user.name or 'Usuário'}</strong>,</p>
                
                <div class="alert">
                    <h3>Você consumiu <strong>80%</strong> dos seus tokens disponíveis!</h3>
                    <p>Este é um alerta preventivo para que você possa planejar a compra de mais créditos.</p>
                </div>
                
                <div class="stats">
                    <h4>📊 Situação Atual:</h4>
                    <ul>
                        <li><strong>Tokens restantes:</strong> {user.remaining_tokens:,}</li>
                        <li><strong>Total de tokens:</strong> {user.total_tokens:,}</li>
                        <li><strong>Percentual usado:</strong> {user.usage_percentage:.1f}%</li>
                    </ul>
                </div>
                
                <h3>💳 Como comprar mais créditos:</h3>
                <ol>
                    <li>Envie um email para: <strong>{self.credits_email}</strong></li>
                    <li>Informe quantos tokens deseja comprar</li>
                    <li>Aguarde confirmação e instruções de pagamento</li>
                    <li>Após o pagamento, os créditos são adicionados automaticamente</li>
                </ol>
                
                <p style="text-align: center;">
                    <a href="mailto:{self.credits_email}?subject=Compra de Tokens - {user.email}" class="button">
                        📧 Solicitar Créditos
                    </a>
                </p>
                
                <p><strong>⏱️ Processamento:</strong> Até 24 horas úteis</p>
                
                <div class="footer">
                    <p>Este é um email automático do sistema IA SOLARIS.<br>
                    Para dúvidas, entre em contato conosco.</p>
                    <p>Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_alert_80_text(self, user) -> str:
        """Template texto para alerta de 80%"""
        return f"""
        ALERTA DE CONSUMO - IA SOLARIS
        
        Olá {user.name or 'Usuário'},
        
        Você consumiu 80% dos seus tokens disponíveis!
        
        Situação Atual:
        - Tokens restantes: {user.remaining_tokens:,}
        - Total de tokens: {user.total_tokens:,}
        - Percentual usado: {user.usage_percentage:.1f}%
        
        Como comprar mais créditos:
        1. Envie email para: {self.credits_email}
        2. Informe quantos tokens deseja comprar
        3. Aguarde confirmação e instruções de pagamento
        
        Processamento: Até 24 horas úteis
        
        IA SOLARIS - {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        """
    
    def _get_alert_95_template(self, user) -> str:
        """Template HTML para alerta de 95%"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc3545; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .alert {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 ALERTA CRÍTICO</h1>
                    <h2>IA SOLARIS</h2>
                </div>
                
                <p>Olá <strong>{user.name or 'Usuário'}</strong>,</p>
                
                <div class="alert">
                    <h3>ATENÇÃO: Você consumiu <strong>95%</strong> dos seus tokens!</h3>
                    <p>Seus tokens estão quase esgotados. Compre créditos agora para evitar interrupção do serviço.</p>
                </div>
                
                <div class="stats">
                    <h4>📊 Situação Crítica:</h4>
                    <ul>
                        <li><strong>Tokens restantes:</strong> {user.remaining_tokens:,}</li>
                        <li><strong>Total de tokens:</strong> {user.total_tokens:,}</li>
                        <li><strong>Percentual usado:</strong> {user.usage_percentage:.1f}%</li>
                    </ul>
                </div>
                
                <h3>🚨 AÇÃO URGENTE NECESSÁRIA:</h3>
                <ol>
                    <li><strong>Envie AGORA</strong> um email para: <strong>{self.credits_email}</strong></li>
                    <li>Assunto: "URGENTE - Compra de Tokens"</li>
                    <li>Informe quantos tokens deseja comprar</li>
                    <li>Processamento prioritário em até 4 horas úteis</li>
                </ol>
                
                <p style="text-align: center;">
                    <a href="mailto:{self.credits_email}?subject=URGENTE - Compra de Tokens - {user.email}" class="button">
                        🚨 COMPRAR AGORA
                    </a>
                </p>
                
                <p><strong>⚠️ IMPORTANTE:</strong> Se os tokens se esgotarem completamente, o acesso será bloqueado temporariamente até a compra de novos créditos.</p>
                
                <div class="footer">
                    <p>Este é um email automático do sistema IA SOLARIS.<br>
                    Para dúvidas urgentes, entre em contato conosco.</p>
                    <p>Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_alert_95_text(self, user) -> str:
        """Template texto para alerta de 95%"""
        return f"""
        ALERTA CRÍTICO - IA SOLARIS
        
        Olá {user.name or 'Usuário'},
        
        ATENÇÃO: Você consumiu 95% dos seus tokens!
        
        Situação Crítica:
        - Tokens restantes: {user.remaining_tokens:,}
        - Total de tokens: {user.total_tokens:,}
        - Percentual usado: {user.usage_percentage:.1f}%
        
        AÇÃO URGENTE NECESSÁRIA:
        1. Envie AGORA email para: {self.credits_email}
        2. Assunto: "URGENTE - Compra de Tokens"
        3. Informe quantos tokens deseja comprar
        
        Processamento prioritário: Até 4 horas úteis
        
        IMPORTANTE: Se os tokens se esgotarem, o acesso será bloqueado.
        
        IA SOLARIS - {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        """
    
    def _get_alert_blocked_template(self, user) -> str:
        """Template HTML para alerta de bloqueio"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #6c757d; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .alert {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚫 Conta Bloqueada</h1>
                    <h2>IA SOLARIS</h2>
                </div>
                
                <p>Olá <strong>{user.name or 'Usuário'}</strong>,</p>
                
                <div class="alert">
                    <h3>Seus tokens foram totalmente consumidos!</h3>
                    <p>O acesso ao chat foi temporariamente bloqueado até a compra de novos créditos.</p>
                </div>
                
                <h3>🔄 Para reativar sua conta IMEDIATAMENTE:</h3>
                <ol>
                    <li><strong>Envie email URGENTE</strong> para: <strong>{self.credits_email}</strong></li>
                    <li><strong>Assunto:</strong> "URGENTE - Reativação de Conta - {user.email}"</li>
                    <li>Informe quantos tokens deseja comprar</li>
                    <li>Aguarde confirmação e instruções de pagamento</li>
                    <li>Após pagamento, sua conta será reativada automaticamente</li>
                </ol>
                
                <p style="text-align: center;">
                    <a href="mailto:{self.credits_email}?subject=URGENTE - Reativação de Conta - {user.email}" class="button">
                        🔄 REATIVAR CONTA
                    </a>
                </p>
                
                <p><strong>⚡ Processamento prioritário:</strong> Até 4 horas úteis</p>
                
                <h4>📋 Pacotes de Tokens Disponíveis:</h4>
                <ul>
                    <li><strong>Básico:</strong> 1.000 tokens - R$ 29,90</li>
                    <li><strong>Padrão:</strong> 2.500 tokens - R$ 69,90 (15% desconto)</li>
                    <li><strong>Premium:</strong> 5.000 tokens - R$ 129,90 (25% desconto)</li>
                </ul>
                
                <div class="footer">
                    <p>Este é um email automático do sistema IA SOLARIS.<br>
                    Para reativação urgente, entre em contato conosco.</p>
                    <p>Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_alert_blocked_text(self, user) -> str:
        """Template texto para alerta de bloqueio"""
        return f"""
        CONTA BLOQUEADA - IA SOLARIS
        
        Olá {user.name or 'Usuário'},
        
        Seus tokens foram totalmente consumidos!
        O acesso foi temporariamente bloqueado.
        
        Para reativar IMEDIATAMENTE:
        1. Envie email URGENTE para: {self.credits_email}
        2. Assunto: "URGENTE - Reativação de Conta - {user.email}"
        3. Informe quantos tokens deseja comprar
        
        Processamento prioritário: Até 4 horas úteis
        
        Pacotes Disponíveis:
        - Básico: 1.000 tokens - R$ 29,90
        - Padrão: 2.500 tokens - R$ 69,90 (15% desconto)
        - Premium: 5.000 tokens - R$ 129,90 (25% desconto)
        
        IA SOLARIS - {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        """
    
    def _get_credits_confirmation_template(self, user, tokens_added: int, transaction_id: str) -> str:
        """Template HTML para confirmação de créditos"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Créditos Adicionados</h1>
                    <h2>IA SOLARIS</h2>
                </div>
                
                <p>Olá <strong>{user.name or 'Usuário'}</strong>,</p>
                
                <div class="success">
                    <h3>Seus créditos foram adicionados com sucesso!</h3>
                    <p><strong>{tokens_added:,} tokens</strong> foram creditados em sua conta.</p>
                </div>
                
                <div class="stats">
                    <h4>📊 Situação Atual:</h4>
                    <ul>
                        <li><strong>Tokens adicionados:</strong> {tokens_added:,}</li>
                        <li><strong>Total disponível:</strong> {user.total_tokens:,}</li>
                        <li><strong>Tokens restantes:</strong> {user.remaining_tokens:,}</li>
                        <li><strong>ID da transação:</strong> {transaction_id}</li>
                    </ul>
                </div>
                
                <p>✅ <strong>Sua conta foi reativada</strong> e você já pode usar o chat normalmente.</p>
                
                <p>Obrigado por usar a IA SOLARIS!</p>
                
                <div class="footer">
                    <p>Este é um email automático do sistema IA SOLARIS.<br>
                    Para dúvidas, entre em contato conosco.</p>
                    <p>Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_credits_confirmation_text(self, user, tokens_added: int, transaction_id: str) -> str:
        """Template texto para confirmação de créditos"""
        return f"""
        CRÉDITOS ADICIONADOS - IA SOLARIS
        
        Olá {user.name or 'Usuário'},
        
        Seus créditos foram adicionados com sucesso!
        
        Detalhes:
        - Tokens adicionados: {tokens_added:,}
        - Total disponível: {user.total_tokens:,}
        - Tokens restantes: {user.remaining_tokens:,}
        - ID da transação: {transaction_id}
        
        Sua conta foi reativada e você já pode usar o chat normalmente.
        
        Obrigado por usar a IA SOLARIS!
        
        IA SOLARIS - {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        """

