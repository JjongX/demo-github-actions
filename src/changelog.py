import streamlit as st

def main():
    # Read the changelog.md file
    with open("CHANGELOG.md", "r", encoding="utf-8") as f:
        changelog_content = f.read()
    st.markdown(changelog_content)

if __name__ == "__main__":
    main()
