class ParcelAppDeliveryCard extends HTMLElement {
  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error("ParcelApp card requires an entity.");
    }

    this._config = {
      events_limit: 5,
      show_expected: true,
      show_carrier: true,
      collapsible_events: false,
      ...config,
    };

    if (!this._card) {
      this._card = document.createElement("ha-card");
      this._card.className = "parcelapp-delivery-card";
      this.appendChild(this._card);
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 5;
  }

  _render() {
    if (!this._hass || !this._config || !this._card) {
      return;
    }

    const stateObj = this._hass.states[this._config.entity];
    if (!stateObj) {
      this._card.innerHTML = this._renderError(
        `Entity not found: ${this._config.entity}`
      );
      return;
    }

    const attrs = stateObj.attributes || {};
    if (!attrs.parcelapp_delivery) {
      this._card.innerHTML = this._renderError(
        "Entity is not a ParcelApp delivery sensor."
      );
      return;
    }

    const title = this._buildTitle(stateObj, attrs);
    const expectedLine = this._buildExpected(attrs);
    const events = Array.isArray(attrs.events) ? attrs.events : [];
    const eventsLimit = Number(this._config.events_limit) || 5;
    const visibleEvents = events.slice(0, Math.max(eventsLimit, 1));

    const eventItems = visibleEvents.length
      ? visibleEvents.map((event) => this._renderEvent(event)).join("")
      : '<li class="event-empty">No events yet.</li>';

    const eventsContent = this._config.collapsible_events && events.length > eventsLimit
      ? `
        <details>
          <summary>Show ${events.length} events</summary>
          <ul class="events">${events.map((event) => this._renderEvent(event)).join("")}</ul>
        </details>
      `
      : `<ul class="events">${eventItems}</ul>`;

    this._card.innerHTML = `
      <style>
        .parcelapp-wrap {
          background: linear-gradient(160deg, #131820, #0f131a);
          border-radius: 12px;
          padding: 16px 18px;
          color: #f4f7fb;
        }
        .title {
          font-size: 1.7rem;
          line-height: 1.25;
          font-weight: 800;
          letter-spacing: 0.01em;
          margin: 0 0 10px 0;
          color: #ffffff;
        }
        .expected {
          margin: 0 0 14px 0;
          font-size: 1.05rem;
          font-weight: 700;
          color: #dbe6ff;
        }
        .events {
          margin: 0;
          padding-left: 18px;
        }
        .events li {
          margin: 10px 0;
          line-height: 1.4;
          color: #f1f6ff;
        }
        .event-main {
          font-weight: 700;
          color: #ffffff;
        }
        .event-empty {
          color: #bdc8da;
          list-style: none;
          margin-left: -18px;
        }
        .error {
          padding: 12px 14px;
          color: #b00020;
          font-weight: 600;
        }
        details {
          color: #dbe6ff;
        }
        summary {
          cursor: pointer;
          margin-bottom: 8px;
          font-weight: 600;
        }
      </style>
      <div class="parcelapp-wrap">
        <h2 class="title">${this._escapeHtml(title)}</h2>
        ${expectedLine ? `<p class="expected">${this._escapeHtml(expectedLine)}</p>` : ""}
        ${eventsContent}
      </div>
    `;
  }

  _buildTitle(stateObj, attrs) {
    if (this._config.title) {
      return this._config.title;
    }

    const base =
      attrs.description ||
      attrs.tracking_number ||
      stateObj.attributes.friendly_name ||
      stateObj.entity_id;

    const carrier =
      this._config.show_carrier && typeof attrs.carrier_code === "string"
        ? attrs.carrier_code.toUpperCase()
        : null;

    return carrier ? `${base}, ${carrier}` : base;
  }

  _buildExpected(attrs) {
    if (!this._config.show_expected) {
      return "";
    }

    const start = attrs.timestamp_expected ?? attrs.date_expected;
    const end = attrs.timestamp_expected_end ?? attrs.date_expected_end;
    if (!start && !end) {
      return "";
    }

    const startText = this._formatDateTime(start);
    const endText = this._formatDateTime(end);

    if (start && end) {
      return `Expected: ${startText} - ${endText}`;
    }

    return `Expected: ${startText || endText}`;
  }

  _renderEvent(event) {
    const eventDate = this._formatDateTime(event?.date);
    const eventText = this._escapeHtml(event?.event || "No event");
    const location = event?.location ? ` (${this._escapeHtml(event.location)})` : "";
    return `<li>${this._escapeHtml(eventDate)} - <span class="event-main">${eventText}</span>${location}</li>`;
  }

  _formatDateTime(value) {
    if (value === null || value === undefined || value === "") {
      return "Unknown time";
    }

    let date;
    if (typeof value === "number" && Number.isFinite(value)) {
      date = new Date(value > 9999999999 ? value : value * 1000);
    } else {
      const text = String(value).trim();
      date = new Date(text);
      if (Number.isNaN(date.getTime()) && text.includes(" ")) {
        date = new Date(text.replace(" ", "T"));
      }
    }

    if (Number.isNaN(date.getTime())) {
      return String(value);
    }

    const locale = this._hass?.locale?.language;
    return new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(date);
  }

  _renderError(message) {
    return `<div class="error">${this._escapeHtml(message)}</div>`;
  }

  _escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
}

if (!customElements.get("parcelapp-delivery-card")) {
  customElements.define("parcelapp-delivery-card", ParcelAppDeliveryCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "parcelapp-delivery-card")) {
  window.customCards.push({
    type: "parcelapp-delivery-card",
    name: "ParcelApp Delivery Card",
    description: "A screenshot-style card for a single ParcelApp delivery.",
  });
}
