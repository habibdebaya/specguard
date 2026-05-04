"""
Requirements data for ARP4754B Appendix E (Wheel Brake System).
PSSA inputs from Tables E12, E13, E14.
SPEC outputs from Table E19.
Each entry pairs the verbatim text with its Z3 constraint.
"""

from dataclasses import dataclass

from z3 import Bool, Real, And, Not, Implies


@dataclass
class Req:
    id: str
    text: str
    constraint: object


# ── Symbol table ──

failed_normal_braking      = Bool("failed_normal_braking")
failed_alternate_braking   = Bool("failed_alternate_braking")
lost_elec_input_1          = Bool("lost_elec_input_1")
lost_elec_input_2          = Bool("lost_elec_input_2")
single_failure             = Bool("single_failure")
inadvertent_braking_takeoff = Bool("inadvertent_braking_takeoff")
normal_mode_active         = Bool("normal_mode_active")
alternate_mode_active      = Bool("alternate_mode_active")
normal_mode_failed         = Bool("normal_mode_failed")
failed_hyd_1               = Bool("failed_hyd_1")
failed_hyd_2               = Bool("failed_hyd_2")
bscu_provides_sov_cmd      = Bool("bscu_provides_sov_cmd")
bscu_provides_nmv_cmd      = Bool("bscu_provides_nmv_cmd")
hyd1_enable_on             = Bool("hyd1_enable_on")
alt_emer_ctrl_on           = Bool("alt_emer_ctrl_on")
erroneous_nmv_cmd          = Bool("erroneous_nmv_cmd")
sov_function_inhibited     = Bool("sov_function_inhibited")

p_bscu_loss_braking_cmd    = Real("p_bscu_loss_braking_cmd")
p_bscu_erroneous_cmd       = Real("p_bscu_erroneous_cmd")
p_bscu_loss_sov_cmd        = Real("p_bscu_loss_sov_cmd")
p_bscu_unintended_sasv     = Real("p_bscu_unintended_sasv")
p_loss_normal_hyd_equip    = Real("p_loss_normal_hyd_equip")
p_loss_alt_hyd_equip       = Real("p_loss_alt_hyd_equip")
p_total_loss_decelerate    = Real("p_total_loss_decelerate")


# ── PSSA inputs (Tables E12, E13, E14) ──

PSSA_REQUIREMENTS = [
    Req("E12-1",
        "Airplane electrical power 1 independent from airplane electrical power 2",
        Not(And(lost_elec_input_1, lost_elec_input_2))),

    Req("E12-2",
        "NORMAL Mode braking function independent from ALTERNATE Mode braking function, for total loss failure condition",
        Not(And(failed_normal_braking, failed_alternate_braking))),

    Req("E12-3",
        "The NMVs and their control are independent from the SOV and its control such that no single failure results in uncommanded braking",
        Implies(single_failure, Not(inadvertent_braking_takeoff))),

    Req("E13-1",
        "The probability of BSCU failure resulting in loss of a valid braking command output to the NMV shall not exceed 2.0E-04 per flight",
        p_bscu_loss_braking_cmd <= 2.0e-04),

    Req("E13-2",
        "The probability of BSCU failure resulting in unannunciated erroneous braking command to the NMV shall not exceed 2.0E-04 per flight",
        p_bscu_erroneous_cmd <= 2.0e-04),

    Req("E13-3",
        "The probability of BSCU failure resulting in the loss of command to open the SOV shall not exceed 2.0E-04 per flight",
        p_bscu_loss_sov_cmd <= 2.0e-04),

    Req("E13-4",
        "The probability of BSCU failure resulting in unintended closure of the S/ASV shall not exceed 2.0E-04 per flight",
        p_bscu_unintended_sasv <= 2.0e-04),

    Req("E13-5",
        "The SOV and NMV commands shall be provided by the BSCU upon loss of either airplane electrical power input",
        And(
            Implies(And(lost_elec_input_1, Not(lost_elec_input_2)),
                    And(bscu_provides_sov_cmd, bscu_provides_nmv_cmd)),
            Implies(And(lost_elec_input_2, Not(lost_elec_input_1)),
                    And(bscu_provides_sov_cmd, bscu_provides_nmv_cmd)),
        )),

    Req("E13-6",
        'When "HYD 1 Enable" output is enabled, then "Alt/Emer Ctrl" output shall be disabled',
        Implies(hyd1_enable_on, Not(alt_emer_ctrl_on))),

    Req("E13-7",
        'When "HYD 1 Enable" output is disabled, then "Alt/Emer Ctrl" output shall be enabled',
        Implies(Not(hyd1_enable_on), alt_emer_ctrl_on)),

    Req("E13-8",
        "No single failure shall cause erroneous NMV command and inhibit the SOV function",
        Not(And(erroneous_nmv_cmd, sov_function_inhibited))),

    Req("E14-1",
        "The probability of 'Loss of Normal Braking System Hydraulic Equipment' will be less than 3.3E-05 per flight",
        p_loss_normal_hyd_equip < 3.3e-05),

    Req("E14-2",
        "The probability of 'Loss of Alternate Braking System Hydraulic Equipment' will be less than 3.3E-05 per flight",
        p_loss_alt_hyd_equip < 3.3e-05),
]


# ── Consolidated specification (Table E19) ──

SPEC_REQUIREMENTS = [
    Req("S18-WBS-R-0120",
        "No single failure or event shall cause the complete loss of hydraulic power for both the WBS Normal and Alternate/Emergency Brake Systems",
        Not(And(failed_normal_braking, failed_alternate_braking))),

    Req("S18-WBS-R-0130",
        "No single failure or event shall cause the complete loss of electrical power for both the WBS Normal and Alternate/Emergency Brake Systems",
        Not(And(lost_elec_input_1, lost_elec_input_2))),

    Req("S18-WBS-R-0150",
        "Complete loss of decelerate the wheels on the ground function shall be less probable than 1.0E-07 for a landing",
        p_total_loss_decelerate < 1.0e-07),

    Req("S18-WBS-R-0326",
        "No single failure shall result in inadvertent wheel braking of all wheels during takeoff roll",
        Implies(single_failure, Not(inadvertent_braking_takeoff))),

    Req("S18-WBS-R-2973",
        "Operation of the Alternate/Emergency Brake System shall be precluded when the Normal Brake System is in use",
        Implies(normal_mode_active, Not(alternate_mode_active))),

    Req("S18-WBS-R-3213",
        "Normal Brake System shall be powered from the airplane HYD 1 hydraulic system",
        Implies(failed_hyd_1, failed_normal_braking)),

    Req("S18-WBS-R-3224",
        "Alternate/Emergency Brake System shall be powered from the airplane HYD 2 hydraulic system",
        Implies(failed_hyd_2, failed_alternate_braking)),

    Req("S18-WBS-R-3245",
        "ALTERNATE Mode shall be automatically selected when the NORMAL Mode fails",
        Implies(normal_mode_failed, alternate_mode_active)),

    Req("S18-WBS-R-6104",
        "The probability of BSCU failure resulting in loss of a valid braking command output to the NMV shall not exceed 2.0E-04 per flight",
        p_bscu_loss_braking_cmd <= 2.0e-04),

    Req("S18-WBS-R-6105",
        "The probability of BSCU failure resulting in unannunciated erroneous braking command to the NMV shall not exceed 2.0E-04 per flight",
        p_bscu_erroneous_cmd <= 2.0e-04),

    Req("S18-WBS-R-6106",
        "The probability of BSCU failure resulting in the loss of command to open the SOV shall not exceed 2.0E-04 per flight",
        p_bscu_loss_sov_cmd <= 2.0e-04),

    Req("S18-WBS-R-6107",
        "The probability of BSCU failure resulting in unintended closure of the S/ASV shall not exceed 2.0E-04 per flight",
        p_bscu_unintended_sasv <= 2.0e-04),

    Req("S18-WBS-R-6108",
        "The SOV and NMV commands shall be provided by the BSCU upon loss of either airplane electrical power input",
        And(
            Implies(And(lost_elec_input_1, Not(lost_elec_input_2)),
                    And(bscu_provides_sov_cmd, bscu_provides_nmv_cmd)),
            Implies(And(lost_elec_input_2, Not(lost_elec_input_1)),
                    And(bscu_provides_sov_cmd, bscu_provides_nmv_cmd)),
        )),

    Req("S18-WBS-R-6109",
        'When "HYD 1 Enable" output is enabled, then "Alt/Emer Ctrl" output shall be disabled',
        Implies(hyd1_enable_on, Not(alt_emer_ctrl_on))),

    Req("S18-WBS-R-6110",
        "No single failure shall cause erroneous NMV command and inhibit the SOV function",
        Not(And(erroneous_nmv_cmd, sov_function_inhibited))),

    Req("S18-WBS-R-6111",
        "The probability of 'Loss of Normal Brake System Hydraulic Components' shall be less than 3.3E-05 per flight",
        p_loss_normal_hyd_equip < 3.3e-05),

    Req("S18-WBS-R-6112",
        "The probability of 'Loss of Alternate/Emergency Brake System Hydraulic Components' shall be less than 3.3E-05 per flight",
        p_loss_alt_hyd_equip < 3.3e-05),
]
