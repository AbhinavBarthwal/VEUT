from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google
from livekit.plugins import noise_cancellation
from prompts import AGENT_INSTRUCTIONS, SESSION_INSTRUCTIONS
from tools import (
    detect_installed_upi_apps,
    extract_payment_details,
    detect_linked_bank_accounts,
    open_upi_app_with_details,
    verify_transaction_safety,
    provide_transaction_guidance,
    handle_non_upi_requests,
    get_transaction_status,
    clear_transaction_data,
    check_device_connection,
    setup_android_integration
)

load_dotenv()


class VoicePayAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            llm=google.beta.realtime.RealtimeModel(
                voice="Charon",  # British-sounding voice for butler persona
                temperature=0.3,  # Lower temperature for more consistent, professional responses
                instructions=AGENT_INSTRUCTIONS,
            ),
            tools=[
                detect_installed_upi_apps,
                extract_payment_details,
                detect_linked_bank_accounts,
                open_upi_app_with_details,
                verify_transaction_safety,
                provide_transaction_guidance,
                handle_non_upi_requests,
                get_transaction_status,
                clear_transaction_data,
                check_device_connection,
                setup_android_integration
            ],
        )
        

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
    )

    await session.start(
        room=ctx.room,
        agent=VoicePayAssistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=SESSION_INSTRUCTIONS
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))