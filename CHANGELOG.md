# CHANGELOG

## 1.0.7 (in development)

## 1.0.6 (2025-07-31)
**Resolve the issue with chat initialization**

- What: We have fixed the KeyError that users encountered when clicking the "New Chat" button before the first chat initialization is complete. In addition, we have moved the initialization step to occur before displaying the sidebar.

- Why: To make the UI/UX more intuitive for users and prevent errors when starting a chat. This ensures a smoother experience by eliminating interruptions that could confuse users and disrupt their workflow.

**Resolve the issue with exceeded number of tokens**

- What: We have fixed the "openai.BadRequestError" error resulting from the generation of chat names for long converations. With this update, we have prevented exceeding the input token limit of the chat completions API during long conversations.

- Why: This fix allows users to continue with long chats without encountering this error, thereby enhancing the continuity of conversations and ensuring that users can engage in extended discussions without technical limitations.

**Resolve the issue with the language cookie**

- What: We have fixed the KeyError related to language settings via cookies. By defaulting the language to "Korean" when another option has not been selected and saved as a cookie, we aim to bypass errors ocurring due to the unstable behavior of cookies.

- Why: Users will now be able to use Macrogen Office without errors even when their cookies have been deleted or malformed. This improvement ensures that language settings are consistently applied, providing a more reliable experience.

**Resolve the issue with expired containers when using files attachments**

- What: The `streamlit-openai` package has been updated to fully address the "Container is expired" error, specifically in cases involving file attachments. While the previous fix allowed expired containers to be replaced automatically, we discovered that the error could still occur when a file in an expired container was accessed. This update ensures that expired containers are now replaced before the chatbot attempts to refer to any attached files.

- Why: With this fix, users can now reliably return to Macrogen Office and continue working with both text and file inputs without needing to reset their sessions, further improving session stability and user experience.

## 1.0.5 (2025-07-09)
**Improve saved chat display and widget behavior**

- What: We refined the display of saved chats so they update immediately after saving and fixed the issue where chats without initial context were all labeled "New Chat". Additionally, we improved widget behaviors to ensure chats reset cleanly for a more intuitive experience.

- Why: These changes were made to deliver a smoother, more predictable user experience when managing chats. By addressing these issues, we aim to make chat management more seamless and reduce confusion.

## 1.0.4 (2025-07-07)
**Add an auto-save chat feature**

- What: We have added an auto-save feature so that users no longer have to manually save their chats. Chats are now automatically saved to history by default. We also introduced a "temporary mode" that allows users to disable auto-save if they prefer not to keep any record of their chats.

- Why: These features were implemented to improve usability and align Macrogen Office with modern chat interfaces. Auto-save ensures that important conversations are not lost, while temporary mode respects users’ needs for privacy or momentary sessions.

**Support Microsoft Office files**

- What: We have added support for Microsoft Office files, including `.doc`, `.docx`, `.ppt`, and `.pptx`. Previously, there was a bug that prevented these files from being processed properly for upload or download within Macrogen Office. This issue has been resolved, enabling seamless interaction with these common file types.

- Why: Supporting Microsoft Office formats expands the types of documents users can work with in Macrogen Office, increasing compatibility and making it easier to analyze content directly within the platform.

## 1.0.3 (2025-06-27)
**UI advancements**

- What: We have made several UI improvements to enhance the aesthetics of Macrogen Office. The page navigation is now displayed in a more intuitive and visually appealing way. Additionally, the Macrogen Logo has been added to the interface. Irrelevant white space has been removed to create a cleaner look.

- Why: These changes were implemented to give a more streamlined interface. By refining the design, we aim to boost productivity and satisfaction among employees using Macrogen Office.

## 1.0.2 (2025-06-25)
**Enhance conversation history**

- What: We have improved the conversation history functionality by integrating the latest version of `streamlit-openai`. Users can now save images, downloads, and uploads, in addition to text. Additionally, when loading a saved conversation, the chat will be restored with the model that was used when the chat was originally created.

- Why: These enhancements were made to improve user experience by providing more comprehensive conversation history management and ensuring continuity with previous interactions.

**Resolve the issue with expired containers**

- What: The issue where users encountered the "Container is expired" error has been addressed in the `streamlit-openai` package. This error occurred when users left their chats open and unattended for a long time. With this update, the code interpreter now automatically replaces expired containers.

- Why: Previously, users returning to their chats had to reset their sessions, causing them to lose the previous context. With this update, users can leave Macrogen Office unattended and return after a long time to continue their conversation seamlessly, enhancing the overall user experience.

## 1.0.1 (2025-06-23)
**Introduce the reasoning model**

- What: We have added the o3 reasoning model to Macrogen Office. Users can now choose between the standard GPT model and the reasoning model directly within the interface. This allows for greater flexibility depending on the task—such as deep analysis, critical thinking, or structured problem solving.

- Why: The reasoning model is designed to enhance cognitive depth, structure, and step-by-step reasoning in responses. By offering users the ability to switch between models, we empower them to tailor the AI’s behavior to better suit different use cases, whether conversational, analytical, or research-oriented.

## 1.0.0 (2025-06-16)
**Update to streamlit-openai and the OpenAI Responses API**

- What: We have updated Macrogen Office to use the latest version of the `streamlit-openai` package, which now leverages OpenAI's new Responses API. Key changes include migration from the Assistants API to the new Responses API, ZIP-based chat history loading and saving, attachment of files directly through the chat input box, and improved rendering of streamed messages including code, images, and downloadable files.

- Why: This update was made to stay aligned with OpenAI's API roadmap and offer a more responsive, feature-rich experience to users. The previously used Assistants API is scheduled for deprecation in early 2026. By adopting the Responses API, we benefit from better performance, more stable tool invocation (e.g., file search, code interpreter, custom functions), and a unified format for all content types.

## 2024-10-22
**Add the Whisper API to process audio files**

- What: We have integrated the Whisper API into Macrogen Office, introducing a new feature that allows users to transcribe audio files into text, which is then displayed within the chat interface. Users can upload audio files in the following supported formats: [`.m4a`, `.mp3`, `.webm`, `.mp4`, `.mpga`, `.wav`, `.mpeg`]. However, for audio files recorded on Galaxy devices and encoded in the .m4a format, you may need to re-encode them to the same .m4a format or another supported format due to the unique "moov atoms" structure of Galaxy `.m4a` files.

- Why: This feature was implemented in response to numerous requests from users who wanted to upload and transcribe audio files. By enabling audio-to-text conversion, we aim to enhance user productivity and facilitate easier sharing and analysis of audio content within Macrogen Office.

**Add a changelog page to display the update history**

- What: We have introduced a changelog page in Macrogen Office that dynamically displays the update history by reflecting the contents of the CHANGELOG.md file. This page provides users with a clear and organized view of all significant updates, enhancements, and bug fixes implemented in Macrogen Office.

- Why: This feature was implemented to increase transparency and keep users informed about ongoing improvements to Macrogen Office. By providing a dedicated changelog page, we aim to offer a convenient and accessible way for users to stay updated on new features, bug fixes, and other changes, thereby enhancing their understanding and experience with Macrogen Office.

## 2024-09-03
**Add auto-login**

- What: We have developed an auto-login feature that allows users to be automatically logged into their accounts without manually entering credentials each time they visit Macrogen Office. This feature is based on the user's selection in the cookie consent modal. If users choose to save their cookie preferences, Macrogen Office securely stores their cookie choice and username, providing a seamless and faster sign-in experience.

- Why: This enhancement was made to improve user convenience by reducing the need to repeatedly log in. By integrating auto-login with the cookie consent preferences, we ensure that users have control over their login settings while streamlining access to Macrogen Office.

## 2024-08-23
**Add cookie consent modal**

- What: We have added a cookie consent modal to Macrogen Office, which prompts users to agree to our use of cookies when they first visit the platform. Users can now choose to save their cookie preferences, which are currently used to store language settings and display the page with the appropriate configurations based on their selections.

- Why: This update ensures compliance with data protection regulations, such as GDPR, by informing users about our use of cookies and obtaining their consent. By allowing users to save their preferences, we enhance the user experience by remembering language choices and displaying the platform with the desired settings upon subsequent visits.

## 2024-08-19
**Update the AWS cwagent to collect error logs in AWS CloudWatch**

- What: We have updated the AWS CloudWatch Agent (cwagent) to enable it to collect and monitor error logs more effectively within AWS CloudWatch, ensuring more comprehensive tracking of system issues.

- Why: This update was made to improve our ability to detect, diagnose, and resolve issues within Macrogen Office. By collecting error logs in AWS CloudWatch, we can proactively address problems, enhancing the platform's reliability and performance.

**Validate file types and handle errors for unsupported uploads**

- What: We have implemented validation for uploaded files to ensure that only supported file types can be uploaded to Macrogen Office. If a user attempts to upload an unsupported file type, the system now displays an informative error message, guiding the user to upload a supported format. This focuses on highlighting the ability to upload, process, and chat with files.

- Why: This enhancement was made to prevent issues arising from unsupported file uploads, improving the user experience by providing clear feedback. It also helps maintain system integrity by ensuring only compatible files are processed, enabling users to effectively upload, process, and chat with supported files within Macrogen Office.

## 2024-08-13
**Resolve the issue with the invalid salt error during login**

- What: We have resolved an issue where users were encountering an "invalid salt" error during login attempts. This error was preventing some users from accessing their accounts. Additionally, we have enhanced the overall readability and clarity of error messages displayed to users during login and other processes, making them more informative and user-friendly.

- Why: This update was made to fix critical login problems that were preventing users from accessing their accounts, ensuring smooth access to Macrogen Office. Improving the clarity of error messages enhances the user experience by providing understandable guidance when issues occur, allowing users to resolve problems more easily.

## 2024-08-01
**Add `.hwp` support**

- What: We have added support for `.hwp` files, which are documents created with Hancom Office. Users can now upload and process `.hwp` files directly within Macrogen Office, enabling them to chat about the content of these files within Macrogen Office's chat interface.

- Why: This feature was implemented to accommodate users, particularly those at Macrogen HQ, who frequently use the `.hwp` format. By expanding Macrogen Office’s compatibility with various file types, we aim to enhance user convenience and support a broader range of document formats for uploading, processing, and communication within Macrogen Office

## 2024-07-15
**Add `.xls` support**

- What: We have introduced support for `.xls` files, the older Excel file format, enabling users to upload and process `.xls` files directly within Macrogen Office. Users can now chat about the content of these files without needing to convert them to newer formats.

- Why: This enhancement was made to provide compatibility with older Excel file formats, addressing the needs of users who rely on `.xls` files. Since OpenAI's APIs do not natively support `.xls` files, we implemented this feature to increase the platform’s utility and ensure seamless handling of documents for uploading, processing, and chatting within Macrogen Office.

## 2024-07-02
**Initial beta release**
