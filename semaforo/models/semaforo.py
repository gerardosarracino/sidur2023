from odoo import models, fields, api, exceptions


class ReportesAnexosop(models.TransientModel):
    _name = "reportes.anexos"

    @api.multi
    def imprimir_accion_excel_anexop1(self):
        url = "/reporte_anexop1"
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    @api.multi
    def imprimir_accion_excel_anexop2(self):
        url = "/reporte_anexop2"
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    @api.multi
    def imprimir_accion_excel_anexop3(self):
        url = "/reporte_anexop3"
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    @api.multi
    def imprimir_accion_excel_anexop4(self):
        url = "/reporte_anexop4"
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    @api.multi
    def imprimir_accion_excel_anexop7(self):
        url = "/reporte_anexop7"
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }