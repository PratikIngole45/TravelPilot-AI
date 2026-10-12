from typing import Dict, Any, List, Optional
from decimal import Decimal, ROUND_HALF_UP
from app.schemas.itinerary import TransitGuidance, TransitOption
from app.core.logging import logger


class TransitRouterService:
    """
    Deterministic transit routing service that provides:
    1. Intercity transit options (Air, Train, Road Bus, Self-Drive / Cab)
    2. Estimated distance & travel durations
    3. Estimated transit price ranges per person and group
    4. Weather and seasonal travel advisories
    """

    # Verified transit corridors database with hubs, distances, and price benchmarks
    CORRIDORS: Dict[str, Dict[str, Any]] = {
        # Goa Corridors
        ("mumbai", "goa"): {
            "distance_km": 590,
            "recommended": "By Train (Vande Bharat / Tejas Express) or Air",
            "options": [
                {
                    "mode": "air",
                    "label": "By Air (Fastest)",
                    "route": "BOM (Mumbai) ➔ GOI (Dabolim) or GOX (Mopa Airport)",
                    "duration": "1h 15m flight (+2h airport)",
                    "cost_pp": 3500.0,
                    "advantages": "Fastest door-to-door transit; multiple daily direct flights.",
                    "advice": "Mopa (North Goa) is best for Candolim/Anjuna; Dabolim is closer to South Goa."
                },
                {
                    "mode": "train",
                    "label": "By Train (Scenic & Budget-Friendly)",
                    "route": "CSMT / Panvel ➔ Madgaon (MAO) / Thivim via Konkan Railway",
                    "duration": "8h - 10h (Vande Bharat: 7h 45m)",
                    "cost_pp": 1100.0,
                    "advantages": "Spectacular Western Ghats scenery, comfortable sleeper / CC coaches.",
                    "advice": "Book Vande Bharat Express or Mandovi Express on IRCTC well in advance."
                },
                {
                    "mode": "road_bus",
                    "label": "By Overnight Sleeper Bus",
                    "route": "Mumbai ➔ NH 66 / Pune-Bengaluru NH 48 ➔ Panaji",
                    "duration": "12h - 14h overnight",
                    "cost_pp": 900.0,
                    "advantages": "Saves hotel night; flexible boarding points across Mumbai.",
                    "advice": "Opt for AC Multi-Axle Volvo / Scania sleeper operators (IntrCity, KSRTC)."
                },
                {
                    "mode": "cab",
                    "label": "By Self-Drive / Private Cab",
                    "route": "Mumbai ➔ Expressway ➔ Pune ➔ Satara ➔ Kolhapur ➔ Chorla Ghat ➔ Goa",
                    "duration": "11h - 12h drive",
                    "cost_pp": 1800.0,
                    "advantages": "Full road-trip freedom with luggage convenience.",
                    "advice": "Avoid coastal NH 66 bypass sections at night due to ongoing road expansion."
                }
            ],
            "advisories": [
                "Konkan Railway tracks operate under special monsoon speed restrictions from June 10 to October 31.",
                "Pre-paid GoaMiles taxis are available at both Dabolim and Mopa airport arrival gates."
            ]
        },
        ("pune", "goa"): {
            "distance_km": 450,
            "recommended": "By Overnight Train or AC Sleeper Bus",
            "options": [
                {
                    "mode": "train",
                    "label": "By Train (Direct)",
                    "route": "Pune Junction (PUNE) ➔ Madgaon (MAO) / Vasco",
                    "duration": "9h - 11h (Goa Express)",
                    "cost_pp": 650.0,
                    "advantages": "Direct overnight connection arriving early morning.",
                    "advice": "Goa Express (12780) departs Pune late afternoon and reaches early morning."
                },
                {
                    "mode": "road_bus",
                    "label": "By AC Sleeper Bus",
                    "route": "Pune (Swargate / Wakad) ➔ NH 48 ➔ Kolhapur ➔ Nipani ➔ Amboli Ghat ➔ Panaji",
                    "duration": "9h - 10h overnight",
                    "cost_pp": 800.0,
                    "advantages": "Frequent departure options from 8 PM to 11 PM every night.",
                    "advice": "Book via verified operators; scenic descent through Amboli Ghat in the morning."
                },
                {
                    "mode": "air",
                    "label": "By Air (Direct)",
                    "route": "PNQ (Pune) ➔ GOX (Mopa) / GOI (Dabolim)",
                    "duration": "1h 05m flight",
                    "cost_pp": 2800.0,
                    "advantages": "Direct nonstop connection; under 70 mins flight time.",
                    "advice": "Direct daily flights by IndiGo and SpiceJet operate to Mopa and Dabolim."
                },
                {
                    "mode": "cab",
                    "label": "By Self-Drive / Road Trip",
                    "route": "Pune ➔ Satara ➔ Kolhapur ➔ Sankeshwar ➔ Gadhinglaj ➔ Amboli ➔ Goa",
                    "duration": "8h - 9h drive",
                    "cost_pp": 1400.0,
                    "advantages": "Smooth 6-lane highway up to Nipani with excellent food stops near Kolhapur.",
                    "advice": "Take the Amboli Ghat route for the smoothest road surface."
                }
            ],
            "advisories": [
                "Amboli Ghat experiences heavy fog and waterfall crowds during peak monsoon weekends."
            ]
        },
        ("delhi", "goa"): {
            "distance_km": 1900,
            "recommended": "By Air (Direct Flights)",
            "options": [
                {
                    "mode": "air",
                    "label": "By Air (Recommended)",
                    "route": "DEL (IGI Airport Delhi) ➔ GOX (Mopa) / GOI (Dabolim)",
                    "duration": "2h 35m nonstop flight",
                    "cost_pp": 5500.0,
                    "advantages": "Only feasible option for 2 to 4-day trip durations.",
                    "advice": "Book 3–4 weeks in advance during winter holiday peak (Dec–Jan)."
                },
                {
                    "mode": "train",
                    "label": "By Train (Rajdhani Express)",
                    "route": "Hazrat Nizamuddin (NZM) ➔ Madgaon (MAO) via Goa Rajdhani",
                    "duration": "26h - 28h",
                    "cost_pp": 3200.0,
                    "advantages": "Includes all meals; comfortable long-distance rail journey.",
                    "advice": "Requires 2 full travel days; recommended only for trips of 6+ days."
                }
            ],
            "advisories": [
                "Flights into North Goa (Mopa/GOX) are ideal if staying near Calangute, Anjuna, or Mandrem."
            ]
        },
        ("bengaluru", "goa"): {
            "distance_km": 560,
            "recommended": "By Air or Overnight Train / Volvo Bus",
            "options": [
                {
                    "mode": "air",
                    "label": "By Air (Fastest)",
                    "route": "BLR (Kempegowda) ➔ GOI (Dabolim) / GOX (Mopa)",
                    "duration": "1h 10m flight",
                    "cost_pp": 3000.0,
                    "advantages": "Dozens of daily flights, shortest transit time.",
                    "advice": "Fly into Dabolim for South Goa resorts or Mopa for North Goa beaches."
                },
                {
                    "mode": "train",
                    "label": "By Train (Overnight)",
                    "route": "Yesvantpur (YPR) ➔ Madgaon (MAO) via Vasco Express",
                    "duration": "13h - 14h",
                    "cost_pp": 750.0,
                    "advantages": "Passes directly in front of the spectacular Dudhsagar Waterfalls.",
                    "advice": "The morning arrival window offers the famous view of Dudhsagar Falls from the train."
                },
                {
                    "mode": "road_bus",
                    "label": "By AC Sleeper Bus",
                    "route": "Bengaluru (Majestic / Anand Rao Circle) ➔ Tumkur ➔ Hubballi ➔ Karwar ➔ Panaji",
                    "duration": "11h - 13h overnight",
                    "cost_pp": 1100.0,
                    "advantages": "Convenient overnight timing with comfortable multi-axle coaches.",
                    "advice": "KSRTC Airavat Club Class or SeaBird Tourist are proven reliable operators."
                }
            ],
            "advisories": [
                "Anmod Ghat section between Belagavi and Mollem may have slow truck traffic."
            ]
        },
        # Shimla Corridors (as user specifically asked about Shimla!)
        ("delhi", "shimla"): {
            "distance_km": 350,
            "recommended": "By Train to Kalka + Toy Train, or Direct Volvo Bus",
            "options": [
                {
                    "mode": "train",
                    "label": "By Train: Shatabdi + Heritage Kalka-Shimla Toy Train",
                    "route": "New Delhi (NDLS) ➔ Kalka (KLK) via Shatabdi ➔ Shimla via UNESCO Toy Train",
                    "duration": "4h (Shatabdi) + 5h (Toy Train) = ~9h total",
                    "cost_pp": 1400.0,
                    "advantages": "UNESCO World Heritage mountain railway journey through 102 tunnels and pine forests.",
                    "advice": "Book the Kalka-Shimla Toy Train (Shivalik Deluxe Express) on IRCTC 30 days ahead."
                },
                {
                    "mode": "road_bus",
                    "label": "By Direct Overnight Volvo Bus",
                    "route": "ISBT Kashmiri Gate (Delhi) ➔ NH 44 / NH 5 ➔ Chandigarh ➔ Shimla ISBT",
                    "duration": "8h - 9h overnight",
                    "cost_pp": 1100.0,
                    "advantages": "Direct door-to-door without train changes; drops directly at Shimla.",
                    "advice": "Himachal Road Transport (HRTC) Himsuta Volvos operate directly from ISBT Kashmiri Gate."
                },
                {
                    "mode": "air",
                    "label": "By Air (via Chandigarh Airport)",
                    "route": "DEL ➔ IXC (Chandigarh Airport) ➔ 3.5h taxi drive to Shimla",
                    "duration": "1h flight + 3.5h mountain drive",
                    "cost_pp": 3800.0,
                    "advantages": "Fastest transit for travelers connecting from south or west India.",
                    "advice": "Shimla's own Jubbarhatti Airport (SLV) has limited turboprop flights subject to weather."
                },
                {
                    "mode": "cab",
                    "label": "By Private Taxi / Self-Drive",
                    "route": "Delhi ➔ Murthal ➔ Ambala ➔ Zirakpur Himalayan Expressway ➔ Solan ➔ Shimla",
                    "duration": "7h - 8h drive via NH 5",
                    "cost_pp": 1750.0,
                    "advantages": "Scenic mountain expressway; stop for famous Murthal parathas.",
                    "advice": "Equip vehicle with anti-skid chains if traveling during heavy snowfall in January."
                }
            ],
            "advisories": [
                "Winter snow (Dec–Feb) can cause icy roads near Kufri and the upper Mall Road.",
                "Monsoon rains (July–August) frequently cause landslide detours along NH 5."
            ]
        },
        ("chandigarh", "shimla"): {
            "distance_km": 115,
            "recommended": "By Himalayan Expressway Cab / HRTC Bus",
            "options": [
                {
                    "mode": "cab",
                    "label": "By Private Taxi / Car",
                    "route": "Chandigarh ➔ Himalayan Expressway ➔ Kalka bypass ➔ Solan ➔ Shimla",
                    "duration": "3h - 3.5h drive",
                    "cost_pp": 800.0,
                    "advantages": "Smooth multi-lane mountain expressway for the majority of the route.",
                    "advice": "Pre-paid airport taxis available at Chandigarh Airport."
                },
                {
                    "mode": "train",
                    "label": "By Kalka Toy Train",
                    "route": "Kalka Railway Station ➔ Shimla via Heritage Narrow Gauge",
                    "duration": "5h scenic mountain rail",
                    "cost_pp": 350.0,
                    "advantages": "Classic heritage experience crossing 800+ bridges and mountain curves.",
                    "advice": "Connects directly from morning trains arriving at Kalka."
                },
                {
                    "mode": "road_bus",
                    "label": "By Frequent HRTC Bus",
                    "route": "ISBT Sector 43 Chandigarh ➔ Shimla",
                    "duration": "3.5h - 4h",
                    "cost_pp": 250.0,
                    "advantages": "Buses depart every 30 minutes throughout the day.",
                    "advice": "Ordinary and Deluxe buses available without advance reservation."
                }
            ],
            "advisories": [
                "Fog can reduce visibility on mountain curves during winter mornings."
            ]
        }
    }

    @classmethod
    def get_transit_guidance(
        cls,
        origin_city: Optional[str],
        destination: str,
        party_size: int = 1
    ) -> Optional[TransitGuidance]:
        if not origin_city or not origin_city.strip():
            return None

        origin_clean = origin_city.strip().lower()
        dest_clean = destination.strip().lower()

        # Extract core city name (e.g., 'Goa, India' -> 'goa', 'Shimla, HP' -> 'shimla')
        target_dest = "goa" if "goa" in dest_clean else ("shimla" if "shimla" in dest_clean else dest_clean)
        target_origin = "mumbai" if "mumbai" in origin_clean or "bombay" in origin_clean else (
            "pune" if "pune" in origin_clean else (
                "delhi" if "delhi" in origin_clean or "ncr" in origin_clean else (
                    "bengaluru" if "bengaluru" in origin_clean or "bangalore" in origin_clean else (
                        "chandigarh" if "chandigarh" in origin_clean else origin_clean
                    )
                )
            )
        )

        key = (target_origin, target_dest)
        corridor = cls.CORRIDORS.get(key)

        if not corridor:
            # Generic fallback guidance for unmapped corridors
            return TransitGuidance(
                origin_city=origin_city.title(),
                destination=destination.title(),
                approximate_distance_km=600,
                recommended_mode="By Air or Long-Distance Express Train",
                options=[
                    TransitOption(
                        mode="air",
                        label="By Air",
                        route_summary=f"Major airport near {origin_city.title()} ➔ Nearest airport to {destination.title()}",
                        estimated_duration_hours="2h - 4h (including connections)",
                        estimated_cost_per_person=4500.0,
                        estimated_group_cost=float(Decimal("4500.0") * Decimal(party_size)),
                        key_advantages="Fastest travel mode for cross-country distances.",
                        booking_advice="Search direct flights on airline portals 3 weeks in advance."
                    ),
                    TransitOption(
                        mode="train",
                        label="By Express Train",
                        route_summary=f"{origin_city.title()} Junction ➔ {destination.title()} Main Station",
                        estimated_duration_hours="10h - 16h depending on rail corridor",
                        estimated_cost_per_person=900.0,
                        estimated_group_cost=float(Decimal("900.0") * Decimal(party_size)),
                        key_advantages="Economical and scenic rail transit.",
                        booking_advice="Check reservation status and quotas on IRCTC."
                    )
                ],
                weather_or_seasonal_advisories=[
                    f"Check seasonal weather and highway advisories between {origin_city.title()} and {destination.title()}."
                ]
            )

        # Build options with exact group multipliers
        computed_options: List[TransitOption] = []
        for opt in corridor["options"]:
            cost_pp = Decimal(str(opt["cost_pp"]))
            # If cab mode, cost is per vehicle (up to 4 people), else per person
            if opt["mode"] == "cab":
                vehicles = max(1, (party_size + 3) // 4)
                grp_cost = (cost_pp * Decimal(vehicles)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                grp_cost = (cost_pp * Decimal(party_size)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            computed_options.append(
                TransitOption(
                    mode=opt["mode"],
                    label=opt["label"],
                    route_summary=opt["route"],
                    estimated_duration_hours=opt["duration"],
                    estimated_cost_per_person=float(cost_pp),
                    estimated_group_cost=float(grp_cost),
                    key_advantages=opt["advantages"],
                    booking_advice=opt["advice"]
                )
            )

        return TransitGuidance(
            origin_city=origin_city.title(),
            destination=destination.title(),
            approximate_distance_km=corridor["distance_km"],
            recommended_mode=corridor["recommended"],
            options=computed_options,
            weather_or_seasonal_advisories=corridor.get("advisories", [])
        )
