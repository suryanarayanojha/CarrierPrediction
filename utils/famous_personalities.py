class FamousPersonalities:
    @staticmethod
    def get_personalities():
        return {
            "Albert Einstein": {
                "birth_date": "1879-03-14",
                "actual_career": "Physics/Science",
                "planet_positions": {
                    "Sun": {"house": 10, "sign": 11},  # Pisces
                    "Moon": {"house": 7, "sign": 8},   # Sagittarius
                    "Mars": {"house": 3, "sign": 4},   # Cancer
                    "Mercury": {"house": 9, "sign": 10}, # Aquarius
                    "Jupiter": {"house": 5, "sign": 6},  # Leo
                    "Venus": {"house": 11, "sign": 0},   # Aries
                    "Saturn": {"house": 1, "sign": 2}    # Gemini
                },
                "achievements": "Nobel Prize in Physics, Theory of Relativity"
            },
            "Steve Jobs": {
                "birth_date": "1955-02-24",
                "actual_career": "Technology/Entrepreneurship",
                "planet_positions": {
                    "Sun": {"house": 5, "sign": 6},     # Leo
                    "Moon": {"house": 9, "sign": 10},   # Aquarius
                    "Mars": {"house": 1, "sign": 2},    # Gemini
                    "Mercury": {"house": 4, "sign": 5},  # Cancer
                    "Jupiter": {"house": 7, "sign": 8},  # Sagittarius
                    "Venus": {"house": 3, "sign": 4},    # Cancer
                    "Saturn": {"house": 11, "sign": 0}   # Aries
                },
                "achievements": "Co-founder of Apple Inc., Revolutionized personal computing"
            },
            "Mahatma Gandhi": {
                "birth_date": "1869-10-02",
                "actual_career": "Politics/Social Reform",
                "planet_positions": {
                    "Sun": {"house": 7, "sign": 8},     # Sagittarius
                    "Moon": {"house": 3, "sign": 4},    # Cancer
                    "Mars": {"house": 9, "sign": 10},   # Aquarius
                    "Mercury": {"house": 6, "sign": 7},  # Libra
                    "Jupiter": {"house": 1, "sign": 2},  # Gemini
                    "Venus": {"house": 5, "sign": 6},    # Leo
                    "Saturn": {"house": 11, "sign": 0}   # Aries
                },
                "achievements": "Indian Independence Movement, Non-violent resistance"
            },
            "William Shakespeare": {
                "birth_date": "1564-04-26",
                "actual_career": "Writing/Literature",
                "planet_positions": {
                    "Sun": {"house": 5, "sign": 6},     # Leo
                    "Moon": {"house": 7, "sign": 8},    # Sagittarius
                    "Mars": {"house": 3, "sign": 4},    # Cancer
                    "Mercury": {"house": 5, "sign": 6},  # Leo
                    "Jupiter": {"house": 9, "sign": 10}, # Aquarius
                    "Venus": {"house": 5, "sign": 6},    # Leo
                    "Saturn": {"house": 1, "sign": 2}    # Gemini
                },
                "achievements": "Greatest playwright in English literature, Created numerous iconic works"
            },
            "Mozart": {
                "birth_date": "1756-01-27",
                "actual_career": "Music/Performance",
                "planet_positions": {
                    "Sun": {"house": 7, "sign": 8},     # Sagittarius
                    "Moon": {"house": 5, "sign": 6},    # Leo
                    "Mars": {"house": 9, "sign": 10},   # Aquarius
                    "Mercury": {"house": 7, "sign": 8},  # Sagittarius
                    "Jupiter": {"house": 3, "sign": 4},  # Cancer
                    "Venus": {"house": 5, "sign": 6},    # Leo
                    "Saturn": {"house": 11, "sign": 0}      # Aries
                },
                "achievements": "Prodigy composer, Created masterpieces of classical music"
            },
            "Marie Curie": {
                "birth_date": "1867-11-07",
                "actual_career": "Physics/Science",
                "planet_positions": {
                    "Sun": {"house": 9, "sign": 10},    # Aquarius
                    "Moon": {"house": 6, "sign": 7},    # Libra
                    "Mars": {"house": 1, "sign": 2},    # Gemini
                    "Mercury": {"house": 9, "sign": 10}, # Aquarius
                    "Jupiter": {"house": 5, "sign": 6},  # Leo
                    "Venus": {"house": 8, "sign": 9},    # Capricorn
                    "Saturn": {"house": 3, "sign": 4}    # Cancer
                },
                "achievements": "Nobel Prize in Physics and Chemistry, Discovered radioactivity"
            },
            "Leonardo da Vinci": {
                "birth_date": "1452-04-15",
                "actual_career": "Arts/Creative",
                "planet_positions": {
                    "Sun": {"house": 5, "sign": 6},     # Leo
                    "Moon": {"house": 9, "sign": 10},   # Aquarius
                    "Mars": {"house": 3, "sign": 4},    # Cancer
                    "Mercury": {"house": 5, "sign": 6},  # Leo
                    "Jupiter": {"house": 7, "sign": 8},  # Sagittarius
                    "Venus": {"house": 5, "sign": 6},    # Leo
                    "Saturn": {"house": 1, "sign": 2}    # Gemini
                },
                "achievements": "Renaissance polymath, Master painter, inventor, and scientist"
            },
            "Nelson Mandela": {
                "birth_date": "1918-07-18",
                "actual_career": "Politics/Social Reform",
                "planet_positions": {
                    "Sun": {"house": 10, "sign": 11},   # Pisces
                    "Moon": {"house": 4, "sign": 5},    # Cancer
                    "Mars": {"house": 1, "sign": 2},    # Gemini
                    "Mercury": {"house": 10, "sign": 11}, # Pisces
                    "Jupiter": {"house": 7, "sign": 8},  # Sagittarius
                    "Venus": {"house": 9, "sign": 10},   # Aquarius
                    "Saturn": {"house": 3, "sign": 4}    # Cancer
                },
                "achievements": "First black president of South Africa, Anti-apartheid revolutionary"
            },
            "Bill Gates": {
                "birth_date": "1955-10-28",
                "actual_career": "Technology/Entrepreneurship",
                "planet_positions": {
                    "Sun": {"house": 6, "sign": 7},     # Libra
                    "Moon": {"house": 10, "sign": 11},  # Pisces
                    "Mars": {"house": 2, "sign": 3},    # Gemini
                    "Mercury": {"house": 6, "sign": 7},  # Libra
                    "Jupiter": {"house": 8, "sign": 9},  # Capricorn
                    "Venus": {"house": 5, "sign": 6},    # Leo
                    "Saturn": {"house": 1, "sign": 2}    # Gemini
                },
                "achievements": "Co-founder of Microsoft, Philanthropist, Technology innovator"
            },
            "Florence Nightingale": {
                "birth_date": "1820-05-12",
                "actual_career": "Medical",
                "planet_positions": {
                    "Sun": {"house": 6, "sign": 7},     # Libra
                    "Moon": {"house": 4, "sign": 5},    # Cancer
                    "Mars": {"house": 8, "sign": 9},    # Capricorn
                    "Mercury": {"house": 6, "sign": 7},  # Libra
                    "Jupiter": {"house": 10, "sign": 11}, # Pisces
                    "Venus": {"house": 7, "sign": 8},    # Sagittarius
                    "Saturn": {"house": 2, "sign": 3}    # Gemini
                },
                "achievements": "Founder of modern nursing, Healthcare reformer"
            },
            "Charles Darwin": {
                "birth_date": "1809-02-12",
                "actual_career": "Physics/Science",
                "planet_positions": {
                    "Sun": {"house": 9, "sign": 10},    # Aquarius
                    "Moon": {"house": 5, "sign": 6},    # Leo
                    "Mars": {"house": 3, "sign": 4},    # Cancer
                    "Mercury": {"house": 9, "sign": 10}, # Aquarius
                    "Jupiter": {"house": 7, "sign": 8},  # Sagittarius
                    "Venus": {"house": 8, "sign": 9},    # Capricorn
                    "Saturn": {"house": 1, "sign": 2}    # Gemini
                },
                "achievements": "Theory of Evolution, Natural Selection, Revolutionary biologist"
            },
            "Martin Luther King Jr.": {
                "birth_date": "1929-01-15",
                "actual_career": "Politics/Social Reform",
                "planet_positions": {
                    "Sun": {"house": 7, "sign": 8},     # Sagittarius
                    "Moon": {"house": 3, "sign": 4},    # Cancer
                    "Mars": {"house": 9, "sign": 10},   # Aquarius
                    "Mercury": {"house": 7, "sign": 8},  # Sagittarius
                    "Jupiter": {"house": 1, "sign": 2},  # Gemini
                    "Venus": {"house": 5, "sign": 6},    # Leo
                    "Saturn": {"house": 11, "sign": 0}   # Aries
                },
                "achievements": "Civil Rights Movement leader, Nobel Peace Prize winner"
            }
        }

    @staticmethod
    def get_personality_details(name):
        personalities = FamousPersonalities.get_personalities()
        return personalities.get(name) 