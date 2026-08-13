import json
import os

from utils.tools import (
    play_youtube,
    send_whatsapp,
    open_app,
    open_file
)

from utils.voice_io import listen, speak

from memory_manager import (
    remember_file,
    get_file,
    remember_application,
    get_application,
    remember_contact,
    get_contact,
    remember_personal_fact,
    get_personal_fact,
    get_personal_facts,
    get_last_summary,
    load_permanent_memory
)


def route_command(json_response):

    # =====================================================
    # PARSE GPT RESPONSE
    # =====================================================

    try:
        task_data = json.loads(json_response)

        task = task_data["task"]
        query = task_data["query"]

    except (json.JSONDecodeError, KeyError, TypeError):

        speak("I couldn't understand the command.")
        return


    # =====================================================
    # PLAY YOUTUBE
    # =====================================================

    if task == "play_youtube":

        speak(f"Playing {query}")

        try:
            play_youtube(query)

        except Exception as e:
            print("YouTube error:", e)
            speak("I couldn't play that.")


    # =====================================================
    # SEND WHATSAPP
    # =====================================================

    elif task == "send_whatsapp":

        try:

            contact_name, message = query.split("|", 1)

            contact_name = contact_name.strip().lower()
            message = message.strip()

            
            # Check permanent memory
            phone = get_contact(contact_name)

            
            # Contact not remembered
            if phone is None:

                speak(
                    f"I don't have a phone number saved for "
                    f"{contact_name}."
                )

                speak(
                    f"Please tell me the phone number for "
                    f"{contact_name}."
                )

                # VOICE INPUT
                phone = listen()

                if not phone:

                    speak(
                        "I couldn't hear the phone number. "
                        "I won't send the message."
                    )

                    return

                phone = phone.strip()

                # Save permanently
                remember_contact(
                    contact_name,
                    phone
                )

                speak(
                    f"I've saved {contact_name}'s number."
                )

            
            # Confirmation
            speak(
                f"You are about to send this WhatsApp "
                f"message to {contact_name}. "
                f"The message is: {message}. "
                f"Should I send it?"
            )

            # VOICE CONFIRMATION
            confirmation = listen()

            if not confirmation:

                speak(
                    "I didn't hear your confirmation. "
                    "I won't send the message."
                )

                return

            confirmation = confirmation.lower().strip()
            if confirmation not in [
                "yes",
                "yeah",
                "yep",
                "send",
                "send it",
                "okay",
                "ok"
            ]:

                speak(
                    "Okay, I won't send the message."
                )

                return
            
            # Send
            speak(
                f"Sending the message to {contact_name}."
            )

            send_whatsapp(
                phone,
                message
            )

            speak(
                "WhatsApp message sent."
            )

        except ValueError:

            speak(
                "Please format the WhatsApp command "
                "as contact and message."
            )

        except Exception as e:

            print("WhatsApp error:", e)

            speak(
                "I couldn't send the WhatsApp message."
            )


    # =====================================================
    # OPEN APPLICATION
    # =====================================================

    elif task == "open_app":

        try:

            # CASE 1:
            # User provides application + path
            if "|" in query:

                app_name, app_path = query.split(
                    "|",
                    1
                )

                app_name = app_name.strip().lower()
                app_path = app_path.strip()

                # Check path
                if not os.path.exists(app_path):

                    speak(
                        f"I couldn't find the application "
                        f"at the path you provided."
                    )

                    return

                # Save permanently
                remember_application(
                    app_name,
                    app_path
                )

                speak(
                    f"I've saved the location of "
                    f"{app_name}."
                )

                # Open
                open_app(app_path)

                speak(
                    f"Opening {app_name}."
                )



            # CASE 2:
            # Only application name
            else:

                app_name = query.strip().lower()

                # Look in permanent memory
                app_path = get_application(
                    app_name
                )

    
                # Application NOT remembered
                if app_path is None:

                    speak(
                        f"I don't know where {app_name} "
                        f"is installed."
                    )

                    speak(
                        f"Please tell me the full path "
                        f"to {app_name}."
                    )

                    # VOICE INPUT
                    app_path = listen()

                    if not app_path:

                        speak(
                            "I couldn't hear the application "
                            "path. I won't open it."
                        )

                        return

                    app_path = app_path.strip()

                    # Verify path
                    if not os.path.exists(app_path):

                        speak(
                            "The path you provided does "
                            "not exist."
                        )

                        return

                    # Save permanently
                    remember_application(
                        app_name,
                        app_path
                    )

                    speak(
                        f"I've saved the location of "
                        f"{app_name}."
                    )


    
                # Application IS remembered
                if not os.path.exists(app_path):

                    speak(
                        f"I remember where {app_name} is "
                        f"installed, but the application "
                        f"is no longer at that location."
                    )

                    return

                # Open
                open_app(app_path)

                speak(
                    f"Opening {app_name}."
                )


        except Exception as e:

            print(
                "Application error:",
                e
            )

            speak(
                "I couldn't open the application."
            )


    # =====================================================
    # OPEN FILE
    # =====================================================

    elif task == "open_file":

        try:


            # CASE 1:
            # File name + path
            if "|" in query:

                file_name, file_path = query.split(
                    "|",
                    1
                )

                file_name = file_name.strip().lower()
                file_path = file_path.strip()

                # Check file
                if not os.path.exists(file_path):

                    speak(
                        f"I couldn't find the file "
                        f"at the path you provided."
                    )

                    return

                # Save permanently
                remember_file(
                    file_name,
                    file_path
                )

                speak(
                    f"I've saved the location of "
                    f"{file_name}."
                )

                # Open
                open_file(file_path)

                speak(
                    f"Opening {file_name}."
                )



            # CASE 2:
            # Only file name
            else:

                file_name = query.strip().lower()

                # Look in permanent memory
                file_path = get_file(
                    file_name
                )

    
                # File NOT remembered
                if file_path is None:

                    speak(
                        f"I don't have a location saved "
                        f"for {file_name}."
                    )

                    speak(
                        "Please tell me the full path "
                        "to the file."
                    )

                    # VOICE INPUT
                    file_path = listen()

                    if not file_path:

                        speak(
                            "I couldn't hear the file path."
                        )

                        return

                    file_path = file_path.strip()

                    # Verify
                    if not os.path.exists(file_path):

                        speak(
                            "The file path you provided "
                            "does not exist."
                        )

                        return

                    # Save permanently
                    remember_file(
                        file_name,
                        file_path
                    )

                    speak(
                        f"I've saved the location of "
                        f"{file_name}."
                    )


    
                # Check remembered path
                if not os.path.exists(file_path):

                    speak(
                        f"I remember the location of "
                        f"{file_name}, but the file is no "
                        f"longer there."
                    )

                    return

                # Open
                open_file(file_path)

                speak(
                    f"Opening {file_name}."
                )


        except Exception as e:

            print(
                "File error:",
                e
            )

            speak(
                "I couldn't open the file."
            )


    # =====================================================
    # REMEMBER
    # =====================================================

    elif task == "remember":

        try:

            key, value = query.split("|", 1)

            key = key.strip().lower()
            value = value.strip()

            if not key or not value:

                speak(
                    "I couldn't understand what you wanted "
                    "me to remember."
                )
                return

            remember_personal_fact(
                key,
                value
            )

            readable_key = key.replace("_", " ")

            speak(
                f"I'll remember that your "
                f"{readable_key} is {value}."
            )

        except ValueError:

            speak(
                "I couldn't understand what you wanted "
                "me to remember."
            )

        except Exception as e:

            print(
                "Memory error:",
                e
            )

            speak(
                "I couldn't save that information."
            )


    # =====================================================
    # RECALL PERMANENT MEMORY
    # =====================================================

    elif task == "recall":

        memory = load_permanent_memory()

        files = memory.get(
            "files",
            {}
        )

        applications = memory.get(
            "applications",
            {}
        )

        contacts = memory.get(
            "contacts",
            {}
        )

        personal_facts = memory.get(
            "personal_facts",
            {}
        )


        # Recall one specific personal fact
        requested_memory = query.strip().lower()

        if requested_memory != "all":

            value = get_personal_fact(
                requested_memory
            )

            if value:

                readable_key = requested_memory.replace(
                    "_",
                    " "
                )

                speak(
                    f"Your {readable_key} is {value}."
                )

                return

            speak(
                "I don't have that information saved."
            )

            return

        
        # Recall everything
        if (
            not files
            and not applications
            and not contacts
            and not personal_facts
        ):

            speak(
                "I don't have any permanent memories yet."
            )

            return

        speak(
            "Here is what I have stored."
        )

        # Personal facts
        if personal_facts:

            speak(
                "Personal information."
            )

            for key, value in personal_facts.items():

                readable_key = key.replace(
                    "_",
                    " "
                )

                speak(
                    f"{readable_key}: {value}"
                )

        # Files
        if files:

            speak("Saved files.")

            for name, path in files.items():

                speak(
                    f"{name}: {path}"
                )

        # Applications
        if applications:

            speak("Saved applications.")

            for name, path in applications.items():

                speak(
                    f"{name}: {path}"
                )

        # Contacts
        if contacts:

            speak("Saved contacts.")

            for name, phone in contacts.items():

                speak(
                    f"{name}: {phone}"
                )


    # =====================================================
    # PREVIOUS CHAT SUMMARY
    # =====================================================

    elif task == "recall_summary":

        summary = get_last_summary()

        if summary:

            speak(
                "Here's what we did in the previous session."
            )

            speak(summary)

        else:

            speak(
                "I don't have a summary from a previous "
                "session yet."
            )


    # =====================================================
    # GENERAL CHAT
    # =====================================================

    elif task == "general_chat":

        speak(query)


    # =====================================================
    # UNKNOWN TASK
    # =====================================================

    else:

        speak(
            "Sorry, I don't recognize that task."
        )