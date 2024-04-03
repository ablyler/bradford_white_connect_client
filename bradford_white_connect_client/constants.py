BRADFORD_WHITE_APP_ID = "BW-Bw-id"
# trunk-ignore(bandit/B105)
BRADFORD_WHITE_APP_SECRET = "BW-1rzhJw2BsALGBW2PVLTqaJIn-yE"


class BradfordWhiteConnectHeatingModes:
    HYBRID = 0
    ELECTRIC = 1
    HEAT_PUMP = 2
    HYBRID_PLUS = 3
    VACATION = 4

    @classmethod
    def is_valid(cls, value):
        return value in {
            cls.HYBRID,
            cls.ELECTRIC,
            cls.HEAT_PUMP,
            cls.HYBRID_PLUS,
            cls.VACATION,
        }
