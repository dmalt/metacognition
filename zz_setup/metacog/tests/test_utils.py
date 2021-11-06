from utils import FrozenBIDSPath, BIDSPathTemplate
import pytest


@pytest.fixture
def froszen_bp():
    return FrozenBIDSPath(subject="foo")


@pytest.fixture
def template_bp():
    return BIDSPathTemplate(subject="foo", template_vars=["task"])


def test_FrosenBIDSPath_delegates_attributes(froszen_bp):
    froszen_bp.subject


def test_FrozenBIDSPath_doesnt_change_on_update(froszen_bp):
    froszen_bp.update(subject="bar")
    assert froszen_bp.subject == "foo"


def test_FrozenBIDSPath_updates_attributes(froszen_bp):
    bp_bar = froszen_bp.update(subject="bar")
    assert bp_bar.subject == "bar"


def test_FrosenBIDSPath_returns_self_on_copy(froszen_bp):
    assert froszen_bp.copy() is froszen_bp


def test_TemplateBIDSPath_fpath_argument_check_and_result(template_bp):
    with pytest.raises(TypeError):
        template_bp.fpath()
    with pytest.raises(TypeError):
        template_bp.fpath(subject="test", task="test")
    assert str(template_bp.fpath(task="test")) == "sub-foo/sub-foo_task-test"


def test_TemplateBIDSPath_template_vars_set(template_bp):
    assert template_bp.template_vars == set(["task"])


def test_TemplateBIDSPath_template_vars_are_readonly(template_bp):
    with pytest.raises(AttributeError):
        template_bp.template_vars = "foo"


def test_TemplateBIDSPath_unhappy_about_nonbids_templates():
    with pytest.raises(ValueError):
        BIDSPathTemplate(subject="foo", template_vars=["foo"])


def test_TemplateBIDSPath_update_normal_vars():
    bp = BIDSPathTemplate(subject="foo", template_vars=["task"])
    new_bp = bp.update(subject="bar")
    assert new_bp.subject == "bar"
    assert bp.subject == "foo"
    assert new_bp.template_vars == set(["task"])
    conflict_template_bp = bp.update(task=None)
    assert conflict_template_bp.template_vars == set()
    conflict_template_bp = bp.update(task="baz")
    assert conflict_template_bp.template_vars == set()


def test_TemplateBIDSPath_update_template_vars_directly():
    bp = BIDSPathTemplate(subject="foo", template_vars=["task"])
    new_bp = bp.update(template_vars=["run"])
    assert new_bp.template_vars == set(["run"])
    assert bp.template_vars == set(["task"])


def test_TemplateBIDSPath_update_template_vars_via_normal_vars():
    bp = BIDSPathTemplate(subject="foo", template_vars=["task", "run"])
    new_bp = bp.update(task="test")
    assert new_bp.template_vars == set(["run"])
    assert bp.template_vars == set(["task", "run"])
    bp.fpath(run=1, task="test")
    new_bp.fpath(run=1)
