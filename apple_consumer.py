"""
Apple Consumer Module
Models the conversational logic and interactive simulation of processing and 'eating' an apple,
providing digital nutrition metrics, bite management, and humor logging.
"""

class AppleConsumer:
    """
    Simulates the process of consuming an apple with state tracking,
    bite counters, crunch sounds, and nutritional analysis.
    """
    def __init__(self, variety: str = "Honeycrisp", size: str = "medium"):
        self.variety = variety
        self.size = size
        self.bites_taken = 0
        self.max_bites = 5 if size == "large" else (4 if size == "medium" else 3)
        self.is_eaten = False
        self.history = []

    def can_eat(self, washed: bool = True, rotten: bool = False) -> bool:
        """
        Returns True if there is still apple left to consume, 
        it is washed, and not rotten.
        """
        if not washed or rotten:
            return False
        return not self.is_eaten and self.bites_taken < self.max_bites

    def eat_bite(self) -> str:
        """
        Takes a bite out of the apple.
        Returns a descriptive string with a crunch sound effect and status update.
        """
        if self.is_eaten or self.bites_taken >= self.max_bites:
            self.history.append("Attempted to bite an already finished apple core.")
            return "Error: The apple is already gone! You're just munching on the core now."

        self.bites_taken += 1
        
        if self.bites_taken >= self.max_bites:
            self.is_eaten = True
            msg = f"CRUNCH! *chomp* That was the last bite of the {self.variety} apple. Core discarded!"
        else:
            msg = f"CRUNCH! *munch* Delicious bite #{self.bites_taken} of {self.max_bites} from your {self.variety} apple."

        self.history.append(msg)
        return msg

    def get_nutrition_report(self) -> dict:
        """Returns digital nutrition and status metrics for the apple session."""
        percent_remaining = max(0, int(((self.max_bites - self.bites_taken) / self.max_bites) * 100))
        return {
            "variety": self.variety,
            "size": self.size,
            "bites_taken": self.bites_taken,
            "max_bites": self.max_bites,
            "percent_remaining": percent_remaining,
            "is_eaten": self.is_eaten,
            "history": self.history
        }


def process_apple_inquiry(inquiry: str) -> str:
    """
    Processes a natural language inquiry about eating an apple with wit and humor.
    """
    query = inquiry.lower().strip()
    if "can you eat" in query or "eat an apple" in query or "can i eat" in query:
        return (
            "Yes! As an AI, I don't have a biological stomach or teeth, "
            "but I can simulate eating a crisp, juicy apple for you right now. "
            "CRUNCH! *munch* 🍎✨ Delicious!"
        )
    return f"Processed apple inquiry: '{inquiry}'. Apples are great for health and productivity!"
