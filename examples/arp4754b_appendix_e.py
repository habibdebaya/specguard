"""
Comprehensive Z3 encoding of ARP4754B Appendix E (Wheel Brake System).

Three system layers and one alternate formulation:
  - AIRPLANE_REQUIREMENTS       Airplane-level (Table E31)
  - PSSA_REQUIREMENTS           WBS-level analysis claims (Tables E12, E13, E14)
  - ALT_PSSA_REQUIREMENTS       WBS PSSA restated as failure rates (Table E28 WBS PSSA ASMP)
  - SPEC_REQUIREMENTS           WBS-level specification (Tables E15, E16, E18 timing, E19)
  - BSCU_PSSA_REQUIREMENTS      BSCU-level analysis claims (Table E22)
  - BSCU_ASSUMPTIONS_TO_WBS     BSCU assumptions communicated to WBS (Table E23)
  - BSCU_SPEC_REQUIREMENTS      BSCU-level specification (Table E24)

Plus UNIT_RELATIONS, the axiom block carrying the per-flight to per-hour
conversion derived from E.3.3 (5-hour average flight).

Tables omitted because they are evidence or metadata rather than logical
claims: E17 (signal lists), E20 (allocation duplicating E19), E21 (IDAL
assignments without their interpretation rules), E25-E27, E29-E33 (QA
evidence and configuration indices), and the figures.
"""

from dataclasses import dataclass

from z3 import Bool, Real, And, Or, Not, Implies


@dataclass
class Req:
    id: str
    text: str
    constraint: object


# ── Symbol table: failure and event Bools ──

failed_normal_braking       = Bool("failed_normal_braking")
failed_alternate_braking    = Bool("failed_alternate_braking")
lost_elec_input_1           = Bool("lost_elec_input_1")
lost_elec_input_2           = Bool("lost_elec_input_2")
single_failure              = Bool("single_failure")
inadvertent_braking_takeoff = Bool("inadvertent_braking_takeoff")
normal_mode_active          = Bool("normal_mode_active")
alternate_mode_active       = Bool("alternate_mode_active")
normal_mode_failed          = Bool("normal_mode_failed")
failed_hyd_1                = Bool("failed_hyd_1")
failed_hyd_2                = Bool("failed_hyd_2")
both_engine_hyd_failed      = Bool("both_engine_hyd_failed")
complete_loss_wheel_brake   = Bool("complete_loss_wheel_brake")
loss_one_thrust_reverser    = Bool("loss_one_thrust_reverser")

# BSCU command and signal Bools
bscu_provides_sov_cmd       = Bool("bscu_provides_sov_cmd")
bscu_provides_nmv_cmd       = Bool("bscu_provides_nmv_cmd")
hyd1_enable_on              = Bool("hyd1_enable_on")
alt_emer_ctrl_on            = Bool("alt_emer_ctrl_on")
erroneous_nmv_cmd           = Bool("erroneous_nmv_cmd")
sov_function_inhibited      = Bool("sov_function_inhibited")
bscu_brake_outputs_in_use   = Bool("bscu_brake_outputs_in_use")
wbs_status_failure          = Bool("wbs_status_failure")
bscu_maintenance_initiated  = Bool("bscu_maintenance_initiated")

# BSCU channel architecture Bools
channel1_invalid                    = Bool("channel1_invalid")
channel2_invalid                    = Bool("channel2_invalid")
channel2_cmd_normal_ctrl            = Bool("channel2_cmd_normal_ctrl")
wbs_annunciation_out                = Bool("wbs_annunciation_out")
voltage_out_of_spec                 = Bool("voltage_out_of_spec")
power_supply_shutoff                = Bool("power_supply_shutoff")
power_up_test_failed                = Bool("power_up_test_failed")
channel1_phys_indep_channel2        = Bool("channel1_phys_indep_channel2")
cmd_phys_indep_monitor              = Bool("cmd_phys_indep_monitor")
comx_monx_diff_specs                = Bool("comx_monx_diff_specs")
power_supply_state_indep_monitor    = Bool("power_supply_state_indep_monitor")
power_up_self_tests_ch2             = Bool("power_up_self_tests_ch2")
power_up_tests_psm                  = Bool("power_up_tests_psm")


# ── Symbol table: WBS capability and property Bools (Table E19) ──

wbs_has_decelerate_means        = Bool("wbs_has_decelerate_means")
wbs_differential_braking        = Bool("wbs_differential_braking")
wbs_parking_brake               = Bool("wbs_parking_brake")
wbs_autobraking                 = Bool("wbs_autobraking")
wbs_antiskid                    = Bool("wbs_antiskid")
wbs_hyd_brake_control           = Bool("wbs_hyd_brake_control")
wbs_overrides_autobrake_on_crew = Bool("wbs_overrides_autobrake_on_crew")
wbs_radiation_qualified         = Bool("wbs_radiation_qualified")
wbs_controlled_by_bscu          = Bool("wbs_controlled_by_bscu")
each_wheel_separate_hyd_lines   = Bool("each_wheel_separate_hyd_lines")
each_circuit_valves_fuses       = Bool("each_circuit_valves_fuses")
antiskid_prevents_skidding      = Bool("antiskid_prevents_skidding")
has_emergency_accumulator       = Bool("has_emergency_accumulator")
alt_emer_aft_of_uerf            = Bool("alt_emer_aft_of_uerf")
wbs_decelerate_fdal_a           = Bool("wbs_decelerate_fdal_a")
ebu_two_redundant_lanes         = Bool("ebu_two_redundant_lanes")
wbs_two_independent_hyd_sources = Bool("wbs_two_independent_hyd_sources")
wbs_dual_bscu_cmd               = Bool("wbs_dual_bscu_cmd")
wbs_no_rudder_or_nws            = Bool("wbs_no_rudder_or_nws")
wbs_indicates_brake_temp        = Bool("wbs_indicates_brake_temp")
wbs_individual_brake_pressure   = Bool("wbs_individual_brake_pressure")
hyd_pressure_per_analysis       = Bool("hyd_pressure_per_analysis")
wbs_one_normal_mode             = Bool("wbs_one_normal_mode")
wbs_one_alternate_mode          = Bool("wbs_one_alternate_mode")
accumulator_powers_emergency    = Bool("accumulator_powers_emergency")
accumulator_attached_to_hyd2    = Bool("accumulator_attached_to_hyd2")
bscu_cmd_fdal_a                 = Bool("bscu_cmd_fdal_a")
bscu_two_independent_channels   = Bool("bscu_two_independent_channels")
bscu_two_independent_power      = Bool("bscu_two_independent_power")
brake_pedals_indep_rudder       = Bool("brake_pedals_indep_rudder")


# ── Symbol table: BSCU-level capability Bools (Table E24) ──

bscu_controls_meter_valves      = Bool("bscu_controls_meter_valves")
bscu_controls_antiskid_valves   = Bool("bscu_controls_antiskid_valves")
bscu_controls_shutoff_valves    = Bool("bscu_controls_shutoff_valves")
bscu_each_two_command_channels  = Bool("bscu_each_two_command_channels")
bscu_each_channel_has_monitoring = Bool("bscu_each_channel_has_monitoring")
bscu_each_channel_has_control   = Bool("bscu_each_channel_has_control")
bscu_each_channel_indep_power   = Bool("bscu_each_channel_indep_power")
bscu_each_channel_indep_pedal   = Bool("bscu_each_channel_indep_pedal")
bscu_command_channels_indep     = Bool("bscu_command_channels_indep")
bscu_hw_idal_a                  = Bool("bscu_hw_idal_a")
bscu_sw_idal_b                  = Bool("bscu_sw_idal_b")
bscu_radiation_qualified        = Bool("bscu_radiation_qualified")


# ── Symbol table: airplane-level Bools (Table E31) ──

airplane_decelerate_on_ground            = Bool("airplane_decelerate_on_ground")
airplane_decelerate_wheels_on_ground     = Bool("airplane_decelerate_wheels_on_ground")
airplane_pilot_controlled_braking        = Bool("airplane_pilot_controlled_braking")
airplane_autobraking                     = Bool("airplane_autobraking")
airplane_antiskid                        = Bool("airplane_antiskid")
airplane_wbs_status_interface            = Bool("airplane_wbs_status_interface")
airplane_decelerate_wheels_on_gear_retract = Bool("airplane_decelerate_wheels_on_gear_retract")
airplane_decelerate_differentially       = Bool("airplane_decelerate_differentially")
airplane_parking_brake                   = Bool("airplane_parking_brake")
airplane_hydraulic_braking               = Bool("airplane_hydraulic_braking")
airplane_autobrake_override              = Bool("airplane_autobrake_override")
airplane_radiation_qualified             = Bool("airplane_radiation_qualified")
airplane_decelerate_function_fdal_a      = Bool("airplane_decelerate_function_fdal_a")
airplane_has_emergency_accumulator       = Bool("airplane_has_emergency_accumulator")


# ── Symbol table: probabilities, rates, and quantities ──

# Per-flight probabilities (Tables E13, E14, E19)
p_bscu_loss_braking_cmd          = Real("p_bscu_loss_braking_cmd")
p_bscu_erroneous_cmd             = Real("p_bscu_erroneous_cmd")
p_bscu_loss_sov_cmd              = Real("p_bscu_loss_sov_cmd")
p_bscu_unintended_sasv           = Real("p_bscu_unintended_sasv")
p_loss_normal_hyd_equip          = Real("p_loss_normal_hyd_equip")
p_loss_alt_hyd_equip             = Real("p_loss_alt_hyd_equip")
p_seven_or_more_sensors_per_flight = Real("p_seven_or_more_sensors_per_flight")
p_loss_elec_bus_per_flight       = Real("p_loss_elec_bus_per_flight")
p_loss_pedal_per_flight          = Real("p_loss_pedal_per_flight")

# Per-hour failure rates (Table E28 WBS PSSA ASMP)
lambda_loss_elec_bus_per_hour    = Real("lambda_loss_elec_bus_per_hour")
lambda_loss_pedal_per_hour       = Real("lambda_loss_pedal_per_hour")

# Per-landing probabilities (Tables E19, E31)
p_total_loss_decelerate              = Real("p_total_loss_decelerate")
p_complete_loss_wheel_braking_per_landing = Real("p_complete_loss_wheel_braking_per_landing")

# Other quantities
stopping_distance_ft                 = Real("stopping_distance_ft")
accumulator_pressure_psi             = Real("accumulator_pressure_psi")
actuator_response_time_ms            = Real("actuator_response_time_ms")
flight_duration_hours                = Real("flight_duration_hours")


# ── Axioms: unit conversions (E.3.3 and the linear approximation P ≈ λt) ──

UNIT_RELATIONS = [
    flight_duration_hours == 5,
    p_loss_elec_bus_per_flight == lambda_loss_elec_bus_per_hour * flight_duration_hours,
    p_loss_pedal_per_flight == lambda_loss_pedal_per_hour * flight_duration_hours,
]


# ── PSSA inputs, WBS layer (Tables E12, E13, E14) ──

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

    Req("E14-3",
        "The probability of 7 or more wheel speed sensors erroneous or inoperative will be less than 1.0E-07 per flight",
        p_seven_or_more_sensors_per_flight < 1.0e-07),

    Req("E14-4",
        "The probability of loss of an airplane electrical power bus will be less than 1.0E-04 per flight",
        p_loss_elec_bus_per_flight < 1.0e-04),

    Req("E14-5",
        "The probability of loss of a Left brake pedal position input will be less than 1.0E-04 per flight",
        p_loss_pedal_per_flight < 1.0e-04),

    Req("E14-6",
        "Airplane electrical power bus 1 is independent from airplane electrical power bus 2",
        Not(And(lost_elec_input_1, lost_elec_input_2))),

    Req("E14-7",
        "HYD 1 hydraulic system is independent from HYD 2 hydraulic system",
        Not(And(failed_hyd_1, failed_hyd_2))),
]


# ── Alternate WBS PSSA formulation (Table E28 WBS PSSA ASMP block) ──
# Restates Table E14 with entries 4 and 5 converted to per-hour failure rates.
# Bidirectional entailment between PSSA_REQUIREMENTS and ALT_PSSA_REQUIREMENTS
# under UNIT_RELATIONS surfaces the unit-mismatch defect.

ALT_PSSA_REQUIREMENTS = [
    Req("E28-WBS-ASMP-1",
        "The probability of 'Loss of Normal Braking System Hydraulic Equipment' will be less than 3.3E-05 per flight",
        p_loss_normal_hyd_equip < 3.3e-05),

    Req("E28-WBS-ASMP-2",
        "The probability of 'Loss of Alternate Braking System Hydraulic Equipment' will be less than 3.3E-05 per flight",
        p_loss_alt_hyd_equip < 3.3e-05),

    Req("E28-WBS-ASMP-3",
        "The probability of 7 or more wheel speed sensors erroneous or inoperative will be less than 1.0E-07 per flight",
        p_seven_or_more_sensors_per_flight < 1.0e-07),

    Req("E28-WBS-ASMP-4",
        "The failure rate for loss of an airplane electrical power bus will be less than 1.0E-04 per hour of flight",
        lambda_loss_elec_bus_per_hour < 1.0e-04),

    Req("E28-WBS-ASMP-5",
        "The failure rate for loss of a left brake pedal position input will be less than 1.0E-04 per hour of flight",
        lambda_loss_pedal_per_hour < 1.0e-04),

    Req("E28-WBS-ASMP-6",
        "Airplane electrical power bus 1 is independent from airplane electrical power bus 2",
        Not(And(lost_elec_input_1, lost_elec_input_2))),

    Req("E28-WBS-ASMP-7",
        "HYD 1 hydraulic system is independent from HYD 2 hydraulic system",
        Not(And(failed_hyd_1, failed_hyd_2))),
]


# ── WBS specification (Tables E15, E16, E18 timing, E19) ──

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

    Req("S18-WBS-ICD-1002",
        "The brake actuators shall respond to a BSCU command within 5 ms of receiving it",
        actuator_response_time_ms <= 5),

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


# ── BSCU PSSA inputs (Table E22) ──

BSCU_PSSA_REQUIREMENTS = [
    Req("BSCU-001",
        "Channel #1 shall have physical independence from Channel #2",
        channel1_phys_indep_channel2),

    Req("BSCU-002",
        "Within each channel, the command function shall have physical independence from the monitor function",
        cmd_phys_indep_monitor),

    Req("BSCU-003",
        "The COMX software and MONX software shall be developed using different software requirement specifications",
        comx_monx_diff_specs),

    Req("BSCU-004",
        "Within each channel, a power supply monitor shall shutoff the power supply when any voltage is detected to be out of specification",
        Implies(voltage_out_of_spec, power_supply_shutoff)),

    Req("BSCU-005",
        "Within each channel, the operational state of the power supply shall have no effect on the operational state of the power supply monitor",
        power_supply_state_indep_monitor),

    Req("BSCU-006",
        "Upon Channel #1 indicating an 'invalid' state, Channel #2 shall command the 'Normal Control' output",
        Implies(channel1_invalid, channel2_cmd_normal_ctrl)),

    Req("BSCU-007",
        "Upon both Channel #1 and Channel #2 indicating 'invalid' states, the 'HYD 1 Enable' output shall be disabled",
        Implies(And(channel1_invalid, channel2_invalid), Not(hyd1_enable_on))),

    Req("BSCU-008",
        "Upon either Channel #1 or Channel #2 indicating a validity error, a WBS annunciation shall be output from the BSCU",
        Implies(Or(channel1_invalid, channel2_invalid), wbs_annunciation_out)),

    Req("BSCU-009",
        "At power-up the BSCU shall perform a self-test of Channel #2 including the ability to switch control from Channel #1 to Channel #2",
        power_up_self_tests_ch2),

    Req("BSCU-010",
        "At power-up each channel of the BSCU shall implement a test of its power supply monitor",
        power_up_tests_psm),

    Req("BSCU-011",
        "If the power-up test fails, a WBS annunciation shall be output from the BSCU",
        Implies(power_up_test_failed, wbs_annunciation_out)),
]


# ── BSCU PSSA assumptions communicated to WBS level (Table E23) ──

BSCU_ASSUMPTIONS_TO_WBS = [
    Req("E23-1",
        "When 'HYD 1 Enable' is disabled, the BSCU brake control outputs are not used",
        Implies(Not(hyd1_enable_on), Not(bscu_brake_outputs_in_use))),

    Req("E23-2",
        "A BSCU maintenance action will be initiated, if the WBS Status indicates a failure",
        Implies(wbs_status_failure, bscu_maintenance_initiated)),
]


# ── BSCU specification (Table E24) ──

BSCU_SPEC_REQUIREMENTS = [
    Req("S18-BSCU-R-0001",
        "The wheel brake command function of the BSCU shall be developed as FDAL A",
        bscu_cmd_fdal_a),

    Req("S18-BSCU-R-0002",
        "The probability of BSCU failure resulting in loss of a valid braking command output to the NMV shall not exceed 2.0E-04 per flight",
        p_bscu_loss_braking_cmd <= 2.0e-04),

    Req("S18-BSCU-R-0003",
        "The probability of BSCU failure resulting in unannunciated erroneous braking command to the NMV shall not exceed 2.0E-04 per flight",
        p_bscu_erroneous_cmd <= 2.0e-04),

    Req("S18-BSCU-R-0004",
        "The probability of BSCU failure resulting in the loss of command to open the SOV shall not exceed 2.0E-04 per flight",
        p_bscu_loss_sov_cmd <= 2.0e-04),

    Req("S18-BSCU-R-0005",
        "The probability of BSCU failure resulting in unintended closure of the S/ASV shall not exceed 2.0E-04 per flight",
        p_bscu_unintended_sasv <= 2.0e-04),

    Req("S18-BSCU-R-0006",
        "The SOV and NMV commands shall be provided by the BSCU upon loss of either airplane electrical power input",
        And(
            Implies(And(lost_elec_input_1, Not(lost_elec_input_2)),
                    And(bscu_provides_sov_cmd, bscu_provides_nmv_cmd)),
            Implies(And(lost_elec_input_2, Not(lost_elec_input_1)),
                    And(bscu_provides_sov_cmd, bscu_provides_nmv_cmd)),
        )),

    Req("S18-BSCU-R-0007",
        'When "HYD 1 Enable" output is enabled, then "Alt/Emer Ctrl" output shall be disabled',
        Implies(hyd1_enable_on, Not(alt_emer_ctrl_on))),

    Req("S18-BSCU-R-0008",
        "No single failure shall cause erroneous NMV command and inhibit the SOV function",
        Not(And(erroneous_nmv_cmd, sov_function_inhibited))),

    Req("S18-BSCU-R-0009",
        "When 'HYD 1 Enable' is disabled, the BSCU brake control outputs shall be disabled",
        Implies(Not(hyd1_enable_on), Not(bscu_brake_outputs_in_use))),

    Req("S18-BSCU-R-0010",
        "BSCU shall calculate the required hydraulic pressure as a function of weight, autobrake mode, ground speed, wheel rotation, brake temperature and deceleration rate in accordance with graphs given in S18 brake force analysis AAS18-XXX",
        hyd_pressure_per_analysis),

    Req("S18-BSCU-R-0011",
        "BSCU shall control the meter valves",
        bscu_controls_meter_valves),

    Req("S18-BSCU-R-0012",
        "BSCU shall control the anti-skid valves",
        bscu_controls_antiskid_valves),

    Req("S18-BSCU-R-0013",
        "BSCU shall control the shut off valves",
        bscu_controls_shutoff_valves),

    Req("S18-BSCU-R-0027",
        "Each BSCU shall have two command channels",
        bscu_each_two_command_channels),

    Req("S18-BSCU-R-0051",
        "Each BSCU channel shall have a monitoring unit",
        bscu_each_channel_has_monitoring),

    Req("S18-BSCU-R-0075",
        "Each BSCU channel shall have a control unit",
        bscu_each_channel_has_control),

    Req("S18-BSCU-R-0099",
        "Each BSCU channel shall have independent power",
        bscu_each_channel_indep_power),

    Req("S18-BSCU-R-0123",
        "Each BSCU channel shall have independent pedal input to both control and monitoring units",
        bscu_each_channel_indep_pedal),

    Req("S18-BSCU-R-0124",
        "The command channels of each BSCU shall be independent of each other",
        bscu_command_channels_indep),

    Req("S18-BSCU-R-0126",
        "The BSCU hardware shall be developed to IDAL A",
        bscu_hw_idal_a),

    Req("S18-BSCU-R-0127",
        "The BSCU software shall be developed to IDAL B",
        bscu_sw_idal_b),

    Req("S18-BSCU-R-0128",
        "BSCU shall meet safety requirements while operating in an average atmospheric radiation environment per the IEC 62396 standard with an altitude of 40000 feet and a latitude of 45 degrees",
        bscu_radiation_qualified),

    Req("S18-BSCU-R-0201",
        "Channel #1 shall have physical independence from Channel #2",
        channel1_phys_indep_channel2),

    Req("S18-BSCU-R-0202",
        "Within each channel, the command function shall have physical independence from the monitor function",
        cmd_phys_indep_monitor),

    Req("S18-BSCU-R-0203",
        "The COMX software and MONX software shall be developed using different software requirement specifications",
        comx_monx_diff_specs),

    Req("S18-BSCU-R-0204",
        "Within each channel, a power supply monitor shall shutoff the power supply when any voltage is detected to be out of specification",
        Implies(voltage_out_of_spec, power_supply_shutoff)),

    Req("S18-BSCU-R-0205",
        "Within each channel, the operational state of the power supply shall have no effect on the operational state of the power supply monitor",
        power_supply_state_indep_monitor),

    Req("S18-BSCU-R-0206",
        "Upon Channel #1 indicating an 'invalid' state, Channel #2 shall command the 'Normal Control' output",
        Implies(channel1_invalid, channel2_cmd_normal_ctrl)),

    Req("S18-BSCU-R-0207",
        "Upon both Channel #1 and Channel #2 indicating 'invalid' states, the 'HYD 1 Enable' output shall be disabled",
        Implies(And(channel1_invalid, channel2_invalid), Not(hyd1_enable_on))),

    Req("S18-BSCU-R-0208",
        "Upon either Channel #1 or Channel #2 indicating a validity error, a WBS annunciation shall be output from the BSCU",
        Implies(Or(channel1_invalid, channel2_invalid), wbs_annunciation_out)),

    Req("S18-BSCU-R-0209",
        "At power-up, the BSCU shall perform a self-test of Channel #2 including the ability to switch control from Channel #1 to Channel #2",
        power_up_self_tests_ch2),

    Req("S18-BSCU-R-0210",
        "At power-up, each channel of the BSCU shall implement a test of its power supply monitor",
        power_up_tests_psm),

    Req("S18-BSCU-R-0211",
        "If the power-up test fails, a WBS annunciation shall be output from the BSCU",
        Implies(power_up_test_failed, wbs_annunciation_out)),
]


# ── Airplane-level requirements (Table E31) ──

AIRPLANE_REQUIREMENTS = [
    Req("S18-ACFT-R-1000",
        "The S18 airplane shall have a means to decelerate on ground",
        airplane_decelerate_on_ground),

    Req("S18-ACFT-R-1100",
        "The S18 airplane shall have a means to decelerate the wheels on the ground",
        airplane_decelerate_wheels_on_ground),

    Req("S18-ACFT-R-1110",
        "The S18 airplane shall have pilot-controlled wheel braking capability",
        airplane_pilot_controlled_braking),

    Req("S18-ACFT-R-1120",
        "The S18 airplane shall have an autobraking capability during landing and RTO",
        airplane_autobraking),

    Req("S18-ACFT-R-1130",
        "The S18 airplane shall have anti-skid braking",
        airplane_antiskid),

    Req("S18-ACFT-R-1140",
        "The S18 airplane shall provide interface for Wheel Brake System status and annunciations",
        airplane_wbs_status_interface),

    Req("S18-ACFT-R-0181",
        "The S18 airplane shall decelerate the wheels on gear retraction",
        airplane_decelerate_wheels_on_gear_retract),

    Req("S18-ACFT-R-0182",
        "The S18 airplane shall be capable of decelerating the wheels differentially",
        airplane_decelerate_differentially),

    Req("S18-ACFT-R-0183",
        "The S18 airplane shall have a parking brake to prevent airplane motion when parked",
        airplane_parking_brake),

    Req("S18-ACFT-R-0184",
        "The S18 airplane shall have hydraulically driven braking",
        airplane_hydraulic_braking),

    Req("S18-ACFT-R-0185",
        "The S18 airplane shall have an autobrake override that can be initiated by the flight crew",
        airplane_autobrake_override),

    Req("S18-ACFT-R-0186",
        "The S18 airplane shall meet safety requirements while operating in an average atmospheric radiation environment per the IEC 62396 standard with an altitude of 40000 feet and a latitude of 45 degrees",
        airplane_radiation_qualified),

    Req("S18-ACFT-R-0933",
        "The Wheel Brake System decelerate the wheels on the ground function shall be developed as FDAL A",
        airplane_decelerate_function_fdal_a),

    Req("S18-ACFT-R-1322",
        "No single failure or event shall result in the complete loss of wheel brake and the loss of one thrust reverser",
        Not(And(complete_loss_wheel_brake, loss_one_thrust_reverser))),

    Req("S18-ACFT-R-1385",
        "Complete loss of wheel braking shall be less than 1.0E-07 for a landing",
        p_complete_loss_wheel_braking_per_landing < 1.0e-07),

    Req("S18-ACFT-R-1550",
        "Loss of power from both hydraulic subsystems powered by the engines shall not lead to complete loss of wheel braking",
        Implies(both_engine_hyd_failed, Not(complete_loss_wheel_brake))),

    Req("S18-ACFT-R-1551",
        "Wheel Brake System shall include an emergency accumulator to supply hydraulic power to the wheel brakes",
        airplane_has_emergency_accumulator),

    Req("S18-ACFT-R-1552",
        "The Alternate/Emergency Brake System hydraulic equipment and piping shall be installed aft of the engine 1 UERF trajectory envelope",
        alt_emer_aft_of_uerf),

    Req("S18-ACFT-R-1600",
        "Two redundant control lanes shall be provided between the Electric Brake Unit (EBU) and each of the two Alternate/Emergency Meter Valves",
        ebu_two_redundant_lanes),
]


# ── Entailment pairs ──
# Each pair declares that the second collection's claims should follow
# from the first collection's constraints under the axioms.

ENTAILMENT_PAIRS = [
    ("SPEC_REQUIREMENTS", "PSSA_REQUIREMENTS"),
    ("BSCU_SPEC_REQUIREMENTS", "BSCU_PSSA_REQUIREMENTS"),
]


# ── Restatement pairings ──
# Each pair names two requirements that purport to express the same claim
# in different forms. The solver runs bidirectional entailment under the
# axiom block to check that the two are genuinely equivalent.

EQUIVALENCE_MAP = [
    ("E14-1", "E28-WBS-ASMP-1"),
    ("E14-2", "E28-WBS-ASMP-2"),
    ("E14-3", "E28-WBS-ASMP-3"),
    ("E14-4", "E28-WBS-ASMP-4"),
    ("E14-5", "E28-WBS-ASMP-5"),
    ("E14-6", "E28-WBS-ASMP-6"),
    ("E14-7", "E28-WBS-ASMP-7"),
]
