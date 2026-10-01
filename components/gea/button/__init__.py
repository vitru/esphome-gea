import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from esphome.const import CONF_ID
from .. import (
    gea_ns,
    GEAComponent,
    CONF_GEA_ID,
    CONF_ERD,
    enable_gea2_discovery_support,
)

DEPENDENCIES = ["gea"]

CONF_PAYLOAD = "payload"
CONF_DISCOVERY = "discovery"
CONF_SNIFFER = "sniffer"
CONF_SNIFFER = "sniffer"

GEAButton = gea_ns.class_("GEAButton", button.Button, cg.Component)

CONFIG_SCHEMA = (
    button.button_schema(GEAButton)
    .extend(
        {
            cv.GenerateID(CONF_GEA_ID): cv.use_id(GEAComponent),
            cv.Optional(CONF_ERD): cv.hex_uint16_t,
            cv.Optional(CONF_DISCOVERY, default=False): cv.boolean,
            cv.Optional(CONF_SNIFFER, default=False): cv.boolean,
            cv.Optional(CONF_SNIFFER, default=False): cv.boolean,
            # Payload bytes to write when the button is pressed.
            # Accepts a list of integers, e.g. [0x01] or [0x00, 0x02].
            cv.Optional(CONF_PAYLOAD, default=[0x01]): cv.All(
                cv.ensure_list(cv.hex_uint8_t), cv.Length(min=1)
            ),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)


def _validate_button(config):
    if config[CONF_DISCOVERY] and config[CONF_SNIFFER]:
        raise cv.Invalid("gea button cannot be both discovery and sniffer")
    if (config[CONF_DISCOVERY] or config[CONF_SNIFFER]) and CONF_ERD in config:
        raise cv.Invalid("discovery/sniffer buttons cannot also specify erd")
    if not config[CONF_DISCOVERY] and not config[CONF_SNIFFER] and CONF_ERD not in config:
        raise cv.Invalid("gea button requires erd unless discovery: true or sniffer: true")
    return config

CONFIG_SCHEMA = cv.All(CONFIG_SCHEMA, _validate_button)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await button.register_button(var, config)

    hub = await cg.get_variable(config[CONF_GEA_ID])
    cg.add(var.set_parent(hub))
    if config[CONF_DISCOVERY]:
        enable_gea2_discovery_support()
        cg.add(var.set_discovery(True))
    elif config[CONF_SNIFFER]:
        cg.add(var.set_sniffer(True))
    else:
        cg.add(var.set_erd(config[CONF_ERD]))
        for byte_val in config[CONF_PAYLOAD]:
            cg.add(var.add_payload_byte(byte_val))
