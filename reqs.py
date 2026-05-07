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

wbs_has_decelerate_means       = Bool("wbs_has_decelerate_means")
wbs_differential_braking       = Bool("wbs_differential_braking")
wbs_parking_brake              = Bool("wbs_parking_brake")
wbs_autobraking                = Bool("wbs_autobraking")
wbs_antiskid                   = Bool("wbs_antiskid")
wbs_hyd_brake_control          = Bool("wbs_hyd_brake_control")
wbs_overrides_autobrake_on_crew = Bool("wbs_overrides_autobrake_on_crew")
wbs_radiation_qualified        = Bool("wbs_radiation_qualified")
wbs_controlled_by_bscu         = Bool("wbs_controlled_by_bscu")
each_wheel_separate_hyd_lines  = Bool("each_wheel_separate_hyd_lines")
each_circuit_valves_fuses      = Bool("each_circuit_valves_fuses")
antiskid_prevents_skidding     = Bool("antiskid_prevents_skidding")
has_emergency_accumulator      = Bool("has_emergency_accumulator")
alt_emer_aft_of_uerf           = Bool("alt_emer_aft_of_uerf")
wbs_decelerate_fdal_a          = Bool("wbs_decelerate_fdal_a")
ebu_two_redundant_lanes        = Bool("ebu_two_redundant_lanes")
wbs_two_independent_hyd_sources = Bool("wbs_two_independent_hyd_sources")
wbs_dual_bscu_cmd              = Bool("wbs_dual_bscu_cmd")
wbs_no_rudder_or_nws           = Bool("wbs_no_rudder_or_nws")
wbs_indicates_brake_temp       = Bool("wbs_indicates_brake_temp")
wbs_individual_brake_pressure  = Bool("wbs_individual_brake_pressure")
hyd_pressure_per_analysis      = Bool("hyd_pressure_per_analysis")
wbs_one_normal_mode            = Bool("wbs_one_normal_mode")
wbs_one_alternate_mode         = Bool("wbs_one_alternate_mode")
accumulator_powers_emergency   = Bool("accumulator_powers_emergency")
accumulator_attached_to_hyd2   = Bool("accumulator_attached_to_hyd2")
bscu_cmd_fdal_a                = Bool("bscu_cmd_fdal_a")
bscu_two_independent_channels  = Bool("bscu_two_independent_channels")
bscu_two_independent_power     = Bool("bscu_two_independent_power")
brake_pedals_indep_rudder      = Bool("brake_pedals_indep_rudder")

p_bscu_loss_braking_cmd    = Real("p_bscu_loss_braking_cmd")
p_bscu_erroneous_cmd       = Real("p_bscu_erroneous_cmd")
p_bscu_loss_sov_cmd        = Real("p_bscu_loss_sov_cmd")
p_bscu_unintended_sasv     = Real("p_bscu_unintended_sasv")
p_loss_normal_hyd_equip    = Real("p_loss_normal_hyd_equip")
p_loss_alt_hyd_equip       = Real("p_loss_alt_hyd_equip")
p_total_loss_decelerate    = Real("p_total_loss_decelerate")
stopping_distance_ft       = Real("stopping_distance_ft")
accumulator_pressure_psi   = Real("accumulator_pressure_psi")


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

    Req("E13-9",
        "The wheel brake command function of the BSCU shall be developed to FDAL A",
        bscu_cmd_fdal_a),

    Req("E14-1",
        "The probability of 'Loss of Normal Braking System Hydraulic Equipment' will be less than 3.3E-05 per flight",
        p_loss_normal_hyd_equip < 3.3e-05),

    Req("E14-2",
        "The probability of 'Loss of Alternate Braking System Hydraulic Equipment' will be less than 3.3E-05 per flight",
        p_loss_alt_hyd_equip < 3.3e-05),
]


# ── Consolidated specification (Table E19) ──

SPEC_REQUIREMENTS = [
    Req("S18-WBS-R-0020",
        "The Wheel Brake System shall have a means to decelerate the wheels on the ground",
        wbs_has_decelerate_means),

    Req("S18-WBS-R-0021",
        "The Wheel Brake System shall be capable of decelerating the S18 airplane to a complete stop/to taxi speed in 2000 feet when wheel brakes, high lift speed brakes and reverse thrust are available, including when at maximum landing weight",
        stopping_distance_ft <= 2000),

    Req("S18-WBS-R-0041",
        "The Wheel Brake System shall provide directional control on ground by a differential braking function",
        wbs_differential_braking),

    Req("S18-WBS-R-0042",
        "The Wheel Brake System shall provide a parking brake to prevent airplane motion on the ground",
        wbs_parking_brake),

    Req("S18-WBS-R-0043",
        "The Wheel Brake System shall provide autobraking capability during landing and RTO",
        wbs_autobraking),

    Req("S18-WBS-R-0044",
        "The Wheel Brake System shall provide anti-skid braking",
        wbs_antiskid),

    Req("S18-WBS-R-0045",
        "The Wheel Brake System shall provide hydraulic brake control",
        wbs_hyd_brake_control),

    Req("S18-WBS-R-0046",
        "The Wheel Brake System shall override the autobrake when the commanded by the flight crew",
        wbs_overrides_autobrake_on_crew),

    Req("S18-WBS-R-0047",
        "The Wheel Brake System shall meet safety requirements while operating in an average atmospheric radiation environment per the IEC 62396 standard with an altitude of 40000 feet and a latitude of 45 degrees",
        wbs_radiation_qualified),

    Req("S18-WBS-R-0049",
        "The Wheel Brake System shall be controlled and monitored by a computer system called Brake System Control Unit",
        wbs_controlled_by_bscu),

    Req("S18-WBS-R-0050",
        "Each wheel brake shall have separate hydraulic power supply lines",
        each_wheel_separate_hyd_lines),

    Req("S18-WBS-R-0052",
        "Each hydraulic Wheel Brake System circuit shall have meter valves, anti-skid valves and hydraulic fuses",
        each_circuit_valves_fuses),

    Req("S18-WBS-R-0055",
        "Anti-skid system shall be capable to prevent skidding of the tires by reducing the pressure applied to the brakes",
        antiskid_prevents_skidding),

    Req("S18-WBS-R-0062",
        "The Wheel Brake System shall include an emergency accumulator to supply hydraulic power to the wheel brakes",
        has_emergency_accumulator),

    Req("S18-WBS-R-0065",
        "The emergency accumulator shall provide a minimum of 1800 psi",
        accumulator_pressure_psi >= 1800),

    Req("S18-WBS-R-0066",
        "The Alternate/Emergency Brake System hydraulic equipment and piping shall be installed aft of the engine 1 UERF trajectory envelope",
        alt_emer_aft_of_uerf),

    Req("S18-WBS-R-0100",
        "The Wheel Brake System decelerate the wheels on the ground function shall be developed as FDAL A",
        wbs_decelerate_fdal_a),

    Req("S18-WBS-R-0120",
        "No single failure or event shall cause the complete loss of hydraulic power for both the WBS Normal and Alternate/Emergency Brake Systems",
        Not(And(failed_normal_braking, failed_alternate_braking))),

    Req("S18-WBS-R-0130",
        "No single failure or event shall cause the complete loss of electrical power for both the WBS Normal and Alternate/Emergency Brake Systems",
        Not(And(lost_elec_input_1, lost_elec_input_2))),

    Req("S18-WBS-R-0150",
        "Complete loss of decelerate the wheels on the ground function shall be less probable than 1.0E-07 for a landing",
        p_total_loss_decelerate < 1.0e-07),

    Req("S18-WBS-R-0200",
        "Two redundant control lanes shall be provided between the EBU and each of the two Alternate/Emergency Meter Valves",
        ebu_two_redundant_lanes),

    Req("S18-WBS-R-0326",
        "No single failure shall result in inadvertent wheel braking of all wheels during takeoff roll",
        Implies(single_failure, Not(inadvertent_braking_takeoff))),

    Req("S18-WBS-R-0508",
        "The Wheel Brake System shall have at least two independent hydraulic pressure sources",
        wbs_two_independent_hyd_sources),

    Req("S18-WBS-R-0509",
        "The Wheel Brake System shall have dual BSCU command functions",
        wbs_dual_bscu_cmd),

    Req("S18-WBS-R-0510",
        "The rudder and nose wheel steering functions shall not be implemented by the Wheel Brake System",
        wbs_no_rudder_or_nws),

    Req("S18-WBS-R-0631",
        "The Wheel Brake System shall indicate individual brake temperature",
        wbs_indicates_brake_temp),

    Req("S18-WBS-R-0632",
        "The Wheel Brake System shall control individual brake pressure",
        wbs_individual_brake_pressure),

    Req("S18-WBS-R-1613",
        "Hydraulic pressure shall be controlled for weight, autobrake mode, ground speed, wheel rotation, brake temperature and deceleration rate in accordance with graphs given in S18 brake force analysis AAS18-XXX",
        hyd_pressure_per_analysis),

    Req("S18-WBS-R-2971",
        "Wheel Brake System shall have one NORMAL operating mode",
        wbs_one_normal_mode),

    Req("S18-WBS-R-2972",
        "Wheel Brake System shall have one ALTERNATE operating mode",
        wbs_one_alternate_mode),

    Req("S18-WBS-R-2973",
        "Operation of the Alternate/Emergency Brake System shall be precluded when the Normal Brake System is in use",
        Implies(normal_mode_active, Not(alternate_mode_active))),

    Req("S18-WBS-R-2974",
        "An emergency accumulator shall provide hydraulic power for EMERGENCY Wheel Brake System operating mode",
        accumulator_powers_emergency),

    Req("S18-WBS-R-2975",
        "The emergency accumulator shall be attached to the HYD 2 hydraulic line between the Selector Valve and the Alternate/Emergency Meter Valve",
        accumulator_attached_to_hyd2),

    Req("S18-WBS-R-2986",
        "The wheel brake command function of the BSCU shall be developed as FDAL A",
        bscu_cmd_fdal_a),

    Req("S18-WBS-R-2997",
        "The BSCU shall have two independent command channels",
        bscu_two_independent_channels),

    Req("S18-WBS-R-2999",
        "The BSCU shall have two independent electrical power sources",
        bscu_two_independent_power),

    Req("S18-WBS-R-3011",
        "Brake pedals shall be independent from the rudder control",
        brake_pedals_indep_rudder),

    Req("S18-WBS-R-3213",
        "Normal Brake System shall be powered from the airplane's HYD 1 hydraulic system",
        Implies(failed_hyd_1, failed_normal_braking)),

    Req("S18-WBS-R-3224",
        "Alternate/Emergency Brake System shall be powered from the airplane's HYD 2 hydraulic system",
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
