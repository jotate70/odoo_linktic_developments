from odoo import models, fields, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    rtefte_incentivo_vivienda = fields.Float(string='Incentivo empleador para vivienda',
                                             default=0,
                                             help="Este es un incentivo que paga el empleador con destinación exclusiva para inversión "
                                                  "en vivienda. Será contemplado como un ingreso laboral no prestacional. Solo influye en el "
                                                  "cálculo de la retención en la fuente, de manera que debe estar ingresado en el campo de pago "
                                                  "no salarial para que afecte la nómina como un ingreso.")

    rtefte_aportes_vol_pens_empleador = fields.Float(string='Aporte para pensiones voluntarias',
                                                     default=0,
                                                     help="Este es el aporte que el empleador hace a nombre del trabajador como aporte "
                                                          "voluntario a pensiones obligatorias, diferente de los aportes a fondos de pensiones "
                                                          "voluntarias que pueda hacer el trabajador por su cuenta")
