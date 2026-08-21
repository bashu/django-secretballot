from unittest.mock import patch

from django.test import TestCase

from secretballot import enable_voting_on

from .models import AnotherLink
from .models import Link
from .models import NonAutomaticEnabledModel


class SecretBallotManagerTest(TestCase):
    """
    secret_ballot manager should be added to model specified
    in enable_voting_on(). Use `objects` as default for the
    manager's name.
    """

    def test_object_manager_is_added_to_class(self):
        assert any(
            manager.__class__.__name__ == "VotableManager"
            for manager in Link._meta.managers  # noqa: SLF001
        )

    def test_object_manager_with_custom_name(self):
        assert hasattr(AnotherLink, "ballot_custom_manager")

    def test_no_db_access_when_getting_queryset(self):
        with patch("django.db.backends.utils.CursorWrapper") as db_mock:
            db_mock.side_effect = RuntimeError("Tried to access database")

            enable_voting_on(NonAutomaticEnabledModel)

            NonAutomaticEnabledModel.objects.get_queryset()

            db_mock.assert_not_called()
