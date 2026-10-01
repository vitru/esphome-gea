#pragma once

#include "esphome/core/component.h"
#include "esphome/components/button/button.h"
#include "../gea.h"

namespace esphome {
namespace gea {

class GEAButton : public button::Button, public Component {
 public:
  void set_erd(uint16_t erd) { erd_ = erd; }
  void set_parent(GEAComponent *parent) { parent_ = parent; }
  void set_discovery(bool discovery) { discovery_ = discovery; }
  void add_payload_byte(uint8_t b) { payload_.push_back(b); }

  void dump_config() override {
    static const char *const TAG = "button.gea";
    LOG_BUTTON("", "GEA Button", this);
    if (discovery_) {
      ESP_LOGCONFIG(TAG, "  Action: start GEA2 ERD discovery scan");
    } else {
      ESP_LOGCONFIG(TAG, "  ERD: 0x%04X", erd_);
      ESP_LOGCONFIG(TAG, "  Payload: %zuB", payload_.size());
    }
  }

 protected:
  void press_action() override {
    if (!parent_)
      return;
    if (discovery_)
      parent_->start_gea2_discovery();
    else
      parent_->write_erd(erd_, payload_);
  }

  uint16_t erd_{0};
  GEAComponent *parent_{nullptr};
  std::vector<uint8_t> payload_;
  bool discovery_{false};
};

}  // namespace gea
}  // namespace esphome
