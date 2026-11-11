class Graph:
    def __init__(self):
        self.adj = {}          # adjacency list: user -> list of friends

    def add_user(self, name):
        self.adj[name] = []
        print("User " + name + " added.")

    def add_friendship(self, a, b):
        self.adj[a].append(b)
        self.adj[b].append(a)  # undirected edge
        print("Friendship created: " + a + " ↔ " + b)

    def show_friends(self, name):
        print("Friends of " + name + ": " + ", ".join(self.adj[name]))

    def display_network(self):
        print("Network:")
        for user in self.adj:
            print(user + ": " + ", ".join(self.adj[user]))


g = Graph()                      # declare the graph
g.add_user("Ali")
g.add_user("Sara")
g.add_user("Bilal")
g.add_user("Hina")
g.add_friendship("Ali", "Sara")
g.add_friendship("Ali", "Bilal")
g.add_friendship("Sara", "Hina")
g.show_friends("Ali")
g.display_network()
