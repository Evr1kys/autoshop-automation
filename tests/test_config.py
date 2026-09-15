import os
import unittest

from tgbot.data.config import BotConfig


class BotConfigTest(unittest.TestCase):
    def test_empty_environment_is_safe(self):
        self.assertEqual(BotConfig.BOT_TOKEN, os.getenv("BOT_TOKEN", ""))
        self.assertIsInstance(BotConfig.ADMINS, list)
        self.assertIsInstance(BotConfig.CHANNELS_FOR_SUBSCRIBE, list)
        self.assertIsInstance(BotConfig.LOGS_CHANNEL, int)


if __name__ == "__main__":
    unittest.main()
