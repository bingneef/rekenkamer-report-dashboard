def test_focus_first_input(mocker):
    from .input import focus_first_input

    m = mocker.patch('streamlit.components.v1.html')
    script = """
        <script>
            window.parent.document.querySelector('input').focus()
        </script>
    """
    focus_first_input()

    m.assert_called_once_with(script, height=0, width=0)
