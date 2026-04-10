from enum import IntEnum

class DifficultyLevel(IntEnum):
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5

    @property
    def label(self):
        return {
            self.VERY_EASY: "Muy fácil",
            self.EASY: "Fácil",
            self.MEDIUM: "Medio",
            self.HARD: "Difícil",
            self.VERY_HARD: "Muy difícil"
        }[self]