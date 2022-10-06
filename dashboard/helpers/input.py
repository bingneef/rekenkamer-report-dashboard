import streamlit.components.v1 as components

def focus_first_input():
    focus_input = """
        <script>
            window.parent.document.querySelector('input').focus()
        </script>
    """
    components.html(focus_input, height=0, width=0)