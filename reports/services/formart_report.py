from ..types.report import EmailDeliveryReport


def format_report_as_html(report: EmailDeliveryReport) -> str:
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .report {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            .stats {{ margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="report">
            <h2>Relatório de Envio de Emails</h2>
            <p>Usuário: {report.user_email}</p>
            <p>Período: {report.period_start.strftime('%d-%m-%Y %H:%M')} até {report.period_end.strftime('%d-%m-%Y %H:%M')}</p>
            
            <div class="stats">
                <h3>Estatísticas</h3>
                <ul>
                    <li>Total de Emails Enviados: {report.stats.total_sent}</li>
                    <li>Entregas Bem-sucedidas: {report.stats.successful_deliveries}</li>
                    <li>Entregas Falhas: {report.stats.failed_deliveries}</li>
                    <li>Total de Destinatários: {report.stats.total_recipients}</li>
                    <li>Destinatários Únicos: {report.stats.unique_recipients}</li>
                    <li>Tempo Médio de Entrega: {report.stats.average_delivery_time} segundos</li>
                </ul>
            </div>
            
            <div class="recipients">
                <h3>Destinatários Mais Comuns</h3>
                <table>
                    <tr>
                        <th>Email</th>
                        <th>Quantidade</th>
                    </tr>
    """

    for recipient in report.most_common_recipients:
        html += f"""
                    <tr>
                        <td>{recipient['email']}</td>
                        <td>{recipient['count']}</td>
                    </tr>
        """

    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    return html
