import unittest
import emoji

from bot import get_prediction, format_tweet


class TestBot(unittest.TestCase):
    def test_get_prediction(self):
        """
        Test that it gets the prediction
        """

        result = get_prediction()
        self.assertIsNotNone(result)

    def test_format_tweet(self):
        """
        Test the tweet formatting
        """

        data = {
            'home_team': 'Boca',
            'away_team': 'River',
            'competition_cluster': 'Argentina',
            'competition_name': 'Superliga',
            'prediction_per_market': {
                'classic': {
                    'prediction': 'X'
                }
            }
        }
        result = " ".join(format_tweet(data).split())
        expected_result = " ".join("""
            Argentina Superliga: 
            :stadium: Boca - River
            :point_right: Pronóstico: Empate
        """.split())

        self.assertEqual(result, emoji.emojize(expected_result, use_aliases=True))


if __name__ == '__main__':
    unittest.main()
