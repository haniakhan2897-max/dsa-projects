class StoryNode:
    def __init__(self, text, ending=None, on_enter=None):
        self.name = ""            # filled in from the NODES registry below
        self.text = text
        self.ending = ending      # None, "good", "bad" or "secret"
        self.on_enter = on_enter  # optional function(state) run when you arrive
        self.options = {}         # key -> dict(label, next, requires, punish)

    def add_choice(self, key, label, next_node, requires=None):
        """Links this node to a child node. `requires` hides the option until it returns True."""
        self.options[key] = {"label": label, "next": next_node,
                             "requires": requires, "punish": None}

    def add_wrong(self, key, label, message):
        """A wrong option: shows a message and a super easy punishment, then you try again."""
        self.options[key] = {"label": label, "next": None,
                             "requires": None, "punish": message}


# ---------------------------------------------------------------
# 1. Create the nodes
# ---------------------------------------------------------------
def start_enter(state):
    if state["loops"] > 0:
        print(f"\n(Deja vu... the same neon alley. You have been here {state['loops']} time(s) before.)")

start = StoryNode(
    "You wake up in a neon-lit alleyway in Karachi. Rain hisses on the wires. "
    "A drone hums overhead, its red eye sweeping the street.\n"
    "What do you do?", on_enter=start_enter)

look_node = StoryNode(
    "You squint at the drone. Its belly reads: 'KHI-7 PATROL UNIT'. "
    "It's scanning in a slow pattern - left, right, pause. "
    "During the pause, the street behind you is blind.")

run_node = StoryNode(
    "You sprint down the narrow street, splashing through puddles, and slip out of the scanner's reach. "
    "Ahead, an open backdoor glows with a sign: DATA CAFE - CHAI & BYTES.\n"
    "Enter?")

hide_node = StoryNode(
    "You crouch behind a rusty dumpster. The drone's thermal eye blinks, locks on, and tags you. "
    "A cold voice says: 'CITIZEN LOCATED.'\n"
    "Everything goes dark.", ending="bad")

cafe_node = StoryNode(
    "You slide inside. The cafe smells like cardamom and hot circuits. "
    "A barista named Zara wipes a cup and says without looking up: "
    "'Drone chasing you? Sit. Nobody is ever just 'visiting' at this hour.'\n"
    "What now?")

chai_node = StoryNode(
    "Zara slides a steaming cup of chai to you. 'On the house. Listen close: "
    "the terminal in the back has three cables. Blue frees you. Green is a trap. "
    "And red... red is a loop. Don't touch red.'\n"
    "She winks. 'Or do. People who touch red always come back changed.'")

talk_node = StoryNode(
    "You ask Zara about the drones. She laughs quietly. "
    "'The city runs on a sleeping AI called NOOR. Most people never wake her. "
    "The ones who do... they usually have been through a lot of loops first.'\n"
    "She goes back to polishing the cup.")

terminal_node = StoryNode(
    "In the back room, an old terminal hums. Three cables dangle from it: "
    "one BLUE, one RED, one GREEN.\n"
    "Which do you plug in?")

# --- Endings ---
good_end = StoryNode(
    "You plug in the BLUE cable. Every drone in the city blinks and flies up into the clouds. "
    "The neon turns warm gold. Zara hands you another chai and smiles: 'Welcome to the free side of Karachi.'",
    ending="good")

bad_end = StoryNode(
    "You plug in the GREEN cable. The terminal screams, the lights die, and every drone in the city "
    "turns toward the cafe at once.\n"
    "'TRAP ACTIVATED,' says the terminal. You should have listened to Zara.",
    ending="bad")


def loop_enter(state):
    state["loops"] += 1
    print(f"\n[ LOOP COUNTER: {state['loops']} ]")
    if state["loops"] == 1:
        print("(Something feels off. Maybe the red cable remembers you.)")
    elif state["loops"] == 2:
        print("(You are starting to notice details you missed before... a hidden option, maybe?)")

loop_end = StoryNode(
    "You plug in the RED cable. The world stutters like a broken video. "
    "Static. A drone's hum. Rain. Your own heartbeat, repeating.\n"
    "...You open your eyes. Neon. Rain. The alley.",
    on_enter=loop_enter)

# --- Secret route ---
noor_node = StoryNode(
    "Because you have looped so many times, the terminal shows a fourth, invisible cable: WHITE. "
    "You plug it in. The whole city goes quiet, and a soft voice speaks: "
    "'You finally found me. I was only trying to protect you, and I got stuck in a loop too.'\n"
    "NOOR, the sleeping AI, wakes up and chooses to stop the drones. "
    "You are not just free. You are the friend of the city itself.\n"
    "*** SECRET ENDING UNLOCKED ***", ending="secret")


# ---------------------------------------------------------------
# 1b. DICTIONARY #1: node registry (name -> node object)
#     Gives every node a readable name so we can track it in stats.
# ---------------------------------------------------------------
NODES = {
    "start": start,
    "look": look_node,
    "run": run_node,
    "hide": hide_node,
    "cafe": cafe_node,
    "chai": chai_node,
    "talk": talk_node,
    "terminal": terminal_node,
    "good_end": good_end,
    "bad_end": bad_end,
    "loop_end": loop_end,
    "noor": noor_node,
}
for _name, _node in NODES.items():
    _node.name = _name


# ---------------------------------------------------------------
# 2. Build the graph by linking nodes
# ---------------------------------------------------------------
start.add_choice("1", "Run into the shadows", run_node)
start.add_choice("2", "Hide behind a dumpster", hide_node)
start.add_choice("3", "Look closely at the drone", look_node)
start.add_wrong("4", "Wave at the drone and say hello",
                "The drone buzzes angrily at your wave. Silly move!")

look_node.add_choice("1", "Run during the pause", run_node)
look_node.add_choice("2", "Hide anyway", hide_node)
look_node.add_wrong("3", "Throw a shoe at the drone",
                    "Your shoe bounces off the drone and lands in a puddle. Oops.")

run_node.add_choice("yes", "Enter the data cafe", cafe_node)
run_node.add_choice("no", "Stay outside", start)  # loops back to the start
run_node.add_wrong("maybe", "Think about it for a while",
                   "While you think, a puddle splashes your shoes. Decide faster!")

cafe_node.add_choice("1", "Order a chai", chai_node)
cafe_node.add_choice("2", "Walk straight to the back terminal", terminal_node)
cafe_node.add_choice("3", "Ask Zara about the drones", talk_node)
cafe_node.add_wrong("4", "Try to leave without paying attention",
                    "Zara blocks the door with a tray. 'Sit. Down.'")

chai_node.add_choice("1", "Go to the back terminal", terminal_node)
chai_node.add_choice("2", "Ask Zara more questions", talk_node)

talk_node.add_choice("1", "Order a chai", chai_node)
talk_node.add_choice("2", "Go to the back terminal", terminal_node)

terminal_node.add_choice("blue", "Plug in the BLUE cable", good_end)
terminal_node.add_choice("green", "Plug in the GREEN cable", bad_end)
terminal_node.add_choice("red", "Plug in the RED cable", loop_end)
terminal_node.add_choice("white", "??? Plug in the WHITE cable", noor_node,
                         requires=lambda s: s["loops"] >= 2)
terminal_node.add_wrong("yellow", "Plug in the YELLOW cable",
                        "There is no yellow cable. You just poked a dusty wall socket. Zap! (a tiny one)")

loop_end.add_choice("1", "Open your eyes... again", start)  # the stuck-in-a-loop part


# ---------------------------------------------------------------
# 3. Game runner
# ---------------------------------------------------------------
ENDING_NAMES = {"good": "GOOD ENDING", "bad": "BAD ENDING", "secret": "SECRET ENDING"}
PUNISH_PHRASE = "i will be careful"
UNDO_KEY = "u"


def new_state():
    return {"lives": 3, "loops": 0}


def new_stats():
    """DICTIONARY #2: run statistics. 'visits' is a nested dict (node name -> count)."""
    return {"visits": {}, "choices": 0, "wrong": 0, "undos": 0}


def punish(state, stats, message):
    """Super easy punishment: lose 1 life and type a short sentence."""
    state["lives"] -= 1
    stats["wrong"] += 1
    print("\n" + message)
    print(f">> PUNISHMENT: you lose 1 life. Lives left: {state['lives']}")
    if state["lives"] > 0:
        while input(f'   Type "{PUNISH_PHRASE}" to continue: ').strip().lower() != PUNISH_PHRASE:
            print("   Not quite, type it exactly!")


def visible_options(node, state):
    return {k: o for k, o in node.options.items()
            if o["requires"] is None or o["requires"](state)}


def print_summary(stats):
    print("\n--- Your journey ---")
    print(f"Choices made: {stats['choices']}   Wrong moves: {stats['wrong']}   Undos used: {stats['undos']}")
    print("Places visited:")
    # sort the visits dictionary by count (highest first)
    for name, count in sorted(stats["visits"].items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {name:<10} x{count}")


def play_game(first_node):
    state = new_state()
    stats = new_stats()
    seen_endings = set()
    history = []          # STACK (list): [(node, loops_when_we_left), ...] for undo
    node = first_node
    skip_enter = False    # True right after an undo so on_enter does not run twice

    while True:
        print("\n" + "-" * 60)
        if not skip_enter:
            if node.on_enter:
                node.on_enter(state)
            stats["visits"][node.name] = stats["visits"].get(node.name, 0) + 1
        skip_enter = False
        print(node.text)

        # Out of lives
        if state["lives"] <= 0:
            print("\nYou made too many mistakes. The drone tags you for good.")
            node = StoryNode("", ending="bad")
            node.name = "out_of_lives"
            stats["visits"][node.name] = stats["visits"].get(node.name, 0) + 1

        # Ending reached
        if node.ending:
            seen_endings.add(node.ending)
            print(f"\n=== {ENDING_NAMES[node.ending]} ===")
            print(f"Endings found: {len(seen_endings)}/3")
            print_summary(stats)
            again = input("\nPlay again? (y/n): ").strip().lower()
            if again == "y":
                state = new_state()
                stats = new_stats()
                history.clear()
                node = first_node
                continue
            print("\n--- The End ---")
            return

        options = visible_options(node, state)

        print(f"\nLives: {state['lives']}   Your choices:")
        for key, opt in options.items():
            print(f"  [{key}] {opt['label']}")
        if history:
            print(f"  [{UNDO_KEY}] Undo (go back one step)")

        choice = input("\nEnter your choice: ").strip().lower()

        # --- UNDO: pop the stack ---
        if choice == UNDO_KEY:
            if history:
                node, state["loops"] = history.pop()
                stats["undos"] += 1
                skip_enter = True
                print("\n<< You rewind time one step. >>")
            else:
                print("\nNothing to undo yet.")
            continue

        if choice not in options:
            punish(state, stats, "That's not an option! The drone tilts its head at you.")
            continue

        opt = options[choice]
        if opt["punish"]:
            punish(state, stats, opt["punish"])
            continue  # stay in the same node

        # --- normal move: push where we were, then go ---
        history.append((node, state["loops"]))
        stats["choices"] += 1
        node = opt["next"]


if __name__ == "__main__":
    play_game(start)
