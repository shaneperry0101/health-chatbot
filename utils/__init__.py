import chainlit as cl

chatProfile = cl.ChatProfile(
    name="Healthcare Assistant Profile",
    icon="/public/chatbot.png",
    markdown_description="This profile provides **healthcare insights and guidance**, leveraging the expertise of a powerful LLM model. It can assist with general health inquiries, creating wellness plans, and understanding medical concepts.",
    starters=[
        cl.Starter(
            label="Personalized fitness plan",
            message="Can you help me create a fitness plan tailored to my current health status and fitness goals? Start by asking about my lifestyle, health conditions, and preferences.",
            icon="/public/fitness.png",
        ),
        cl.Starter(
            label="Understanding medications",
            message="Explain the side effects and proper usage of a medication like 'Ibuprofen' in simple terms.",
            icon="/public/medication.png",
        ),
        cl.Starter(
            label="Tips for better sleep",
            message="Provide actionable tips to improve sleep quality for someone experiencing insomnia. Ask me about my current sleep habits first.",
            icon="/public/sleep.png",
        ),
        cl.Starter(
            label="Healthy meal planning",
            message="Help me design a weekly meal plan that aligns with a balanced diet and accounts for any dietary restrictions or preferences I might have.",
            icon="/public/nutrition.png",
        )
    ],
)
