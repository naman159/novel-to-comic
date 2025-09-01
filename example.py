#!/usr/bin/env python3
"""
Example usage of the Novel to Comic Generator.

This script demonstrates how to use the NTC system to convert a novel chapter
into a manhwa-style comic.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from main import EnhancedNovelToComic
from config import Secrets

secrets = Secrets()


def main():
    # Check if Vertex AI is properly configured
    if not secrets.GOOGLE_CLOUD_PROJECT:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set!")
        print("Please set your Google Cloud project ID:")
        print("export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("\nAlso ensure you have:")
        print("1. A service account key file path set in GOOGLE_CLOUD_SA_PATH")
        print("2. Vertex AI API enabled in your Google Cloud project")
        print("3. Proper permissions for the service account")
        return

    # Check if service account key file exists
    if not secrets.GOOGLE_CLOUD_SA_PATH:
        print("Error: GOOGLE_CLOUD_SA_PATH environment variable not set!")
        print("Please set your service account key file path:")
        print("export GOOGLE_CLOUD_SA_PATH='path/to/your/sa-key.json'")
        print("\nAlso ensure you have:")
        print("1. A service account key file in the specified location")
        print("2. Vertex AI API enabled in your Google Cloud project")
        print("3. Proper permissions for the service account")
        return

    if not os.path.exists(secrets.GOOGLE_CLOUD_SA_PATH):
        print(
            f"Error: Service account key file '{secrets.GOOGLE_CLOUD_SA_PATH}' not found!"
        )
        print("Please place your service account key file in the specified location.")
        print("See setup_vertexai.md for detailed setup instructions.")
        return

    print(f"✅ Using Google Cloud Project: {secrets.GOOGLE_CLOUD_PROJECT}")
    print("✅ Service account key file found")
    print("Initializing Enhanced Novel to Comic Generator...")
    comic_generator = EnhancedNovelToComic(output_dir="example_comic")

    # Example chapter text
    chapter_text = """
    Jake felt like if he had simply blinked his eyes and then suddenly found himself somewhere entirely different. There was no prompt except the system message, no feeling of being thrown through time and space; he just kind of… moved.

He found himself in a…room? This one was far larger than the one before. Scratch that, calling it a room was a bloody understatement. Despite him being able to see the ceiling, he could only barely make out what seemed like a wall far off in the distance to one of the sides. On the roof was a huge circular light that appeared to act as a sun.

Looking from the ceiling to the wall, this entire place seemed to have some kind of circular design, like a huge dome. He was standing on what he could only identify as a huge pillar, one of many that were spread in all directions.

Where one would expect the floor to be, one instead saw a vast forest spreading out in all directions. Yet none of the trees even reached close to the top of the pillar. Not due to the trees being small, some looked easily over a hundred meters tall, but due to the pillar being so monstrously tall itself.

As he was starting to wonder if the system had somehow forgotten him or what exactly was happening, the trusty window and voice appeared again.

*Welcome to the tutorial*

He felt a warm glow in his entire body as he heard the sound of yet another accompanying notification.

Title earned: [Forerunner of the New World]

A title? One that I assume everyone gets, Jake thought, quickly checking it out.

[Forerunner of the New World] – Complete the introduction and enter the tutorial as a forerunner of the New World. +3 all stats. Grants the skill: [Endless Tongues of the Myriad Races (Unique)].

Three to all stats out of nowhere could only be welcome. Likely also the source of the warm glow from before. Though he still was far from sure exactly how much that would help. The skill, however, was a bit more tangible as he looked at what it did.

[Endless Tongues of the Myriad Races (Unique)] - Allows you to communicate with the myriad races throughout the multiverse. A unique skill granted for free to the forerunners of a newly initiated race.

The skill somehow allowed him to communicate with other races. Was it only speech, or writing too? Again, more questions, and attempting to focus on the skills yielded no further results. He even attempted to use his newly acquired Identify skill, with nothing happening.

Hearing something behind him, he was startled and quickly turned around just to see that someone else had also been transported to the same platform. With a hand on his knife-handle, he noticed who it was.

“Jacob?” he asked rhetorically, looking at the man before him. Jacob was no longer wearing his suit but was instead donned out in chainmail, gauntlets, and what looked like leather pants with a pair of sturdy-looking boots, the entire thing looking like it was taken out of the costume rack from a medieval movie.

Jacob also appeared flummoxed by the entire situation as he took a second or two to collect himself before hearing and seeing Jake.

“Jake!? Oh, man, is it good to see you! Have you seen any of the others?” Jacob asked with his usual high energy in a hopeful voice.

“Nah, I am just as surprised to see you here. After we entered the elevator, did you also – “

But before Jake had a chance to ask, another flash of light appeared, and yet again, before he could even see who it was, another flash of light, and then another, until they were a total of 10 people on the platform before the flashes stopped.

Jake instantly recognized all the people, as 5 of them had been in the elevator with him, and 4 who were other employees at his company. To his relief, Caroline was amongst the new arrivals and looked to be fine, now donning a white robe with what looked like a small wand at her hip.

“What happen-“

“Hey, why-“

“You seen Mike!?”

“Where is-“

Everyone began speaking over each other: all confused, but some more than others. Jake simply stood back as he tried to internally grasp the situation while, of course, listening to the others. After the initial panic had settled, they all calmed down and began assessing their situation. They were all professionals, after all. It had nothing to do with Jacob trying to calm them. Not at all.

After a quick round of questions and answers, it seemed like they had all been transported to their own respective interrogation-like room and had gone through roughly the same ordeal as Jake had. However, Jake did learn that he had apparently missed some questions, as the others had discovered a few more details. One of which was that new skills could be earned every 5 levels with their classes.

As they moved on, they also did a tally on their different classes. They turned out to have 1 light, 2 medium and 1 heavy-variant warrior, 2 archers, 3 casters, and 1 healer. Rather balanced, something Jake suspected the system had done on purpose. Or maybe just luck.

Their armors and outfits also greatly differed. No longer all wearing their nice dress shirts and ‘presentable’ clothes they usually wore. The light warrior having on leather armor, medium warriors, Jacob being one of them, having on his chain-mail set, the heavy warrior wearing what looked like rather poorly made iron armor.

The other archer, whom Jake recognized to be Casper from R&D, had on the same cloak as him, wielding a wooden bow like him also. Casper was one of the few other people Jake always got along with during work. They had to interact a lot due to what they did and naturally hit it off. Both were rather introverted and happened to possess some of the same hobbies. He wasn't sure if he could classify him as a friend, but close acquaintance at least. Also, they both sucked at anything romantic, making them kindred spirits in that department.

Joanna was one of the people panicking the most, with her husband Mike not being amongst them. She herself had chosen to be a caster, perhaps just due to it seemingly being the least physically demanding. Though thinking of it, she once said that she and her kids really liked a certain book about a scarred boy wizard.

He also learned from the conversation that apparently you could have asked for a different weapon in the Introduction, something he had been unaware of. Maybe he could have gotten a modern compound bow… though he doubted it, considering the whole medieval theme going on.

The last two classes were two other casters, all wearing brown robes very similar to the one he had on, seeming to be quite a bit more comfortable, their material more akin to silk. They all had wooden sticks in their hands, something he assumed to be wands. And finally, there was their one healer, Caroline, in her white robe, also seeming to be very silk-like, with her smaller white wand.

Another topic discussed was naturally the skills granted. As Jake expected, everyone had gotten Identify and the translation skill included in the title granted upon entering this so-called tutorial. Class skills were another story though.

Light warriors had a dual-wielding skill, which gave a boost while wielding two weapons, a throwing weapon skill, and a common-rarity skill, the counterpart to Jake's Archer’s Eye called Quickstep, allowing the warrior to make quick bursts of speed. In reality, however, the skill just made one take a step slightly quicker than normal, being thoroughly underwhelming in practice.

The medium warrior had five skills, though all with Inferior rating. They had a skill for one-handed, one for two-handed, one for sword & shield, throwing weapon skill, and an ability called Balanced Approach, which gave a small bonus to all stat effects while wielding any weapon. It was one so small that neither of the two medium warriors could even tell the difference.

The heavy warrior had the same sword & shield skill, a two-handed weapon skill, and a skill called Toughen Up, which allowed the warrior to make the effect of toughness increase temporarily. That too, was incredibly underwhelming, not even having any visual cue at all. Also, Bertram said it still hurt when Jacob jabbed him, making even the effect questionable.

The archer skills Jake already knew, of course.

Casters also had three skills, the first skill called magic-tool proficiency, which allowed them to use their wands and other magic items, an attack skill called Mana Bolt, and a defensive skill called Mana Barrier. The barrier sucked too, being so weak that a casual swipe with a sword could break it, but the mana bolt seemed quite powerful.

The healer class had 3 skills also, one called Heal, which unsurprisingly enough, allowed the healer to heal things, one called Regeneration, which turned out to be a passive aura that allowed allies of the healer to regenerate health faster, and the last skill the same one as the casters allowing them to use magic items. Of these skills, Jake was especially interested in the aura, and how exactly it determined who were allies and who weren't.

Another thing they also determined was that the identification skill didn’t work on other people. It did not even return a basic message. There simply was no response. It seemed that either the rarity of the skill was too low or prohibited for some reason. Jake looked towards Caroline and decided to ask about the aura, but he was interrupted before he had any chance to.

“Everyone! Look at the other platforms. I think there are other people on them,” The heavy warrior Bertram said, grabbing everyone’s attention. As Jake looked over at the nearest platform, his improved vision came in handy, as he was able to make out some details.

There appeared to be 10 individuals on the other platform too, and as he looked around, so were there on all the others around him. He still saw some bursts of light on some of the other platforms, but after a minute or two, it was all silent, and the tutorial started for real.

*Tutorial commencing*

[Tutorial Panel]

Duration: 63 days & 21:47:11

Tutorial Type: Survival

Completion Criteria: Survive the duration of the tutorial

Tutorial rules: Collect Tutorial Points (TP).

Tutorial Information: The Great Forest below is filled with danger and opportunities for the new initiates to experience. Beasts roam the forest, hunting for prey. Kill the beasts to acquire TP while gaining strength. Perhaps even a chance to hunt the Beast Lords will present itself…

Tutorial Point Rules: Gain TP upon killing beasts split amongst the contributors. Upon killing another initiate, half their TP will be split amongst the contributors.

Final Rewards based on TP and the number of Survivors

Total Survivors Remaining: 1200/1200

TP Collected: 0

As Jake read through the information, he suddenly felt the pillar under him shake slightly, as it slowly began being lowered. He quickly collected himself and checked that all his equipment was properly in place. As he did this, he wondered how he could be so calm despite the situation and noticed that everyone else was also oddly calm, even if it did vary from person to person. Perhaps it had something to do with willpower, or more likely it was due to reliance on a certain individual.

Throughout the conversation, Jacob had been the guiding light for everything. He had made sure one person spoke at a time, that useful information was extracted, and that everyone got their turn. It was an unspoken rule that he was the leader of the group. One that Jake, of course, had absolutely no intention of opposing.

The group calmly discussed their plan of action during their descent, Jacob instantly taking the lead once more, of course.

They agreed to focus on the first aspect of this entire thing: Survive. They all had weapons, and all had potions; warriors and archers had 3 health and 3 stamina potions each, while the casters and Caroline had 3 health and 3 mana potions instead.

Besides that, all they had were the clothes on their bodies. The rest of the internal discussion mainly revolved around the tutorial's weird details, such as the seemingly utterly random duration. They also reached an agreement that hunting down beasts was a necessity. None of them was a fan of it, but they had to eat somehow. Based on the tutorial rules, it didn’t appear possible to shy away from violence. They also collectively agreed that they wouldn’t antagonize any other survivors unless they didn't have any other options.

Jake didn’t agree with everything but didn’t want to play devil's advocate or start any unnecessary fights. He had already noticed from before that maybe he was a bit of an outlier. He didn’t really understand the unwillingness to hunt. He himself felt quite excited at the notion.

“First of all, we will have to locate water, food, and shelter. The flora does not appear to be the same as that on earth, so we can’t trust our current knowledge of what is and what isn't safe to eat. We should try to see if the identify skill can help with distinguishing edible from poisonous plants. The system also mentioned beasts, so hunting will likely also be an option, if not necessary, to secure a source of food,” Jacob said. “But we also have to be wary of the other survivors. We shouldn't be aggressive, but let’s not be taken as pushovers either. Chances are we will have to hunt beasts as the system says to get stronger and survive. If we work together and do our best, I am sure we can all make it home safe.”

The small speech was a bit superfluous, considering they had already gone over those points but seemed to get everyone on the same track. Jake was once again reminded of why Jacob was the youngest department chief their company had ever had. He had achieved this, relying solely on his competency and charisma, plus a bit of nepotism, but that was almost expected in the job market in this day and age, or, well, before this day and age.

The only thing that put Jake slightly off was spotting Caroline staring at Jacob with stars in her eyes. Not that this was either the time or place for such silly thoughts. The pillar was getting closer and closer to the ground.

As they finally reached below the crown of the trees, Jake was able to spot several bird-like creatures hiding in the trees, though he was unable to make out any details. Two months… he would have to survive two months in this forest.

When they were only a few meters from the ground, Jake steeled himself for whatever was to come.

The pillar finally reached the ground, and they found themselves in a clearing. The pillar below them oddly seemed to phase through the ground, only leaving grass beneath their feet, leaving no evidence of the massive pillar ever having existed.

Taking a deep breath of the fresh air Jake clenched his fist around his bow. He felt a bit nervous. But more than that, a weird feeling began bubbling up from deep inside of him. Excitement.

His boring world had changed, and he had no intention of making this damn forest his grave.
    """

    print("\n🎬 Processing chapter with Enhanced Features...")
    print("This enhanced version includes:")
    print("   ✅ Intelligent scene analysis and continuity tracking")
    print("   ✅ Advanced redundancy detection and prevention")
    print("   ✅ Smart location consistency management")
    print("   ✅ AI-powered panel count optimization")
    print("\nThis may take several minutes as the AI generates images...")

    try:
        # Process the chapter and generate comic panels
        panel_paths = comic_generator.process_chapter(chapter_text)

        print(f"\n✅ Successfully generated {len(panel_paths)} comic panels!")
        print("\nGenerated panels:")
        for i, path in enumerate(panel_paths):
            print(f"  Panel {i+1}: {path}")

        print(f"\n📁 All assets saved in: {comic_generator.output_dir}")
        print("   - Character images: characters/")
        print("   - Location images: locations/")
        print("   - Comic panels: panels/")
        print("   - Metadata: characters.json, locations.json")

        # Show enhanced features summary
        if hasattr(comic_generator, "narrative_flow"):
            print(f"\n🎭 Enhanced Features Summary:")
            print(
                f"   - Scenes processed: {len(comic_generator.narrative_flow.scene_sequence)}"
            )
            print(
                f"   - Continuity tracking: {'✅ Enabled' if secrets.ENABLE_CONTINUITY_TRACKING else '❌ Disabled'}"
            )
            print(
                f"   - Redundancy detection: {'✅ Enabled' if secrets.ENABLE_REDUNDANCY_DETECTION else '❌ Disabled'}"
            )
            print(
                f"   - Panel optimization: {'✅ Enabled' if hasattr(comic_generator, 'generated_panels') else '❌ Disabled'}"
            )

        print("\n🎉 Your manhwa comic is ready!")

    except Exception as e:
        print(f"\n❌ Error processing chapter: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that your service account has proper permissions")
        print("2. Ensure Vertex AI API is enabled in your Google Cloud project")
        print("3. Verify your service account key file is valid and not expired")
        print("4. Check your internet connection and Google Cloud service status")
        print("\nFor detailed setup instructions, see setup_vertexai.md")


if __name__ == "__main__":
    main()
