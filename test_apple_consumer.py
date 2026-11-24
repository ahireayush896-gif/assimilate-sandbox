import unittest
from apple_consumer import AppleConsumer, process_apple_inquiry

class TestAppleConsumer(unittest.TestCase):
    def test_apple_consumer_initialization(self):
        consumer = AppleConsumer(variety="Granny Smith", size="medium")
        self.assertEqual(consumer.variety, "Granny Smith")
        self.assertEqual(consumer.size, "medium")
        self.assertEqual(consumer.bites_taken, 0)
        self.assertFalse(consumer.is_eaten)
        self.assertTrue(consumer.can_eat(washed=True, rotten=False))
        self.assertFalse(consumer.can_eat(washed=False, rotten=False))
        self.assertFalse(consumer.can_eat(washed=True, rotten=True))

    def test_apple_consumer_eating_flow(self):
        consumer = AppleConsumer(variety="Fuji", size="small")
        self.assertEqual(consumer.max_bites, 3)
        
        bite_1 = consumer.eat_bite()
        self.assertIn("CRUNCH", bite_1)
        self.assertEqual(consumer.bites_taken, 1)
        self.assertTrue(consumer.can_eat())

        consumer.eat_bite()
        consumer.eat_bite()
        self.assertTrue(consumer.is_eaten)
        self.assertFalse(consumer.can_eat())

        extra_bite = consumer.eat_bite()
        self.assertIn("already gone", extra_bite)

    def test_nutrition_report(self):
        consumer = AppleConsumer(variety="Honeycrisp", size="large")
        self.assertEqual(consumer.max_bites, 5)
        consumer.eat_bite()
        report = consumer.get_nutrition_report()
        self.assertEqual(report["variety"], "Honeycrisp")
        self.assertEqual(report["bites_taken"], 1)
        self.assertEqual(report["percent_remaining"], 80)
        self.assertFalse(report["is_eaten"])

    def test_process_apple_inquiry(self):
        response = process_apple_inquiry("can you eat an apple?")
        self.assertIn("Yes", response)
        self.assertIn("CRUNCH", response)

        general_response = process_apple_inquiry("Tell me about fruit")
        self.assertIn("Apples are great", general_response)

if __name__ == "__main__":
    unittest.main()
