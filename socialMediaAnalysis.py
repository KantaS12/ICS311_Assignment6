import datetime
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import re
import math

class User:
    def __init__(self, username, attributes=None):
        self.username = username
        self.attributes = attributes if attributes is not None else {}
        self.connections = defaultdict(list)
        self.posts_authored = []
        self.posts_read = []
        self.comments_made = []

    def add_connection(self, other_user, category):
        self.connections[category].append(other_user)

    def add_post(self, post):
        self.posts_authored.append(post)

    def add_read_post(self, post, view_time):
        self.posts_read.append((post, view_time))

    def add_comment(self, comment):
        self.comments_made.append(comment)

    def __repr__(self):
        return f"User(username='{self.username}')"

class Post:
    def __init__(self, post_id, author, content, creation_time):
        self.post_id = post_id
        self.author = author
        self.content = content
        self.creation_time = creation_time
        self.comments = []
        self.viewers = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_viewer(self, user, view_time):
        self.viewers.append((user, view_time))

    def get_num_comments(self):
        return len(self.comments)

    def get_num_views(self):
        return len(self.viewers)

    def __repr__(self):
        return f"Post(id='{self.post_id}', author='{self.author.username}', created='{self.creation_time.strftime('%Y-%m-%d %H:%M:%S')}')"

class Comment:
    def __init__(self, comment_id, author, post, content, creation_time):
        self.comment_id = comment_id
        self.author = author
        self.post = post
        self.content = content
        self.creation_time = creation_time

    def __repr__(self):
        return f"Comment(id='{self.comment_id}', author='{self.author.username}', post_id='{self.post.post_id}')"
    

class SocialMediaAnalyzer:
    def __init__(self, users, posts):
        self.users = {user.username: user for user in users}
        self.posts = {post.post_id: post for post in posts}
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        for username, user in self.users.items():
            self.graph.add_node(username, type='user', attributes=user.attributes)

        for post_id, post in self.posts.items():
            self.graph.add_node(post_id, type='post', content=post.content,
                                creation_time=post.creation_time)

        for post_id, post in self.posts.items():
            self.graph.add_edge(post.author.username, post_id, relation='authorship')

        for post_id, post in self.posts.items():
            for viewer, view_time in post.viewers:
                self.graph.add_edge(viewer.username, post_id, relation='viewed', view_time=view_time)


        for post_id, post in self.posts.items():
            for comment in post.comments:
                self.graph.add_edge(comment.author.username, post_id, relation='commented_on')

        for username, user in self.users.items():
            for category, connected_users in user.connections.items():
                for connected_user in connected_users:
                    self.graph.add_edge(username, connected_user.username, relation=category)


    def _calculate_post_importance(self, comment_weight=0.5, view_weight=0.5):
        if not (0 <= comment_weight <= 1 and 0 <= view_weight <= 1 and abs(comment_weight + view_weight - 1) < 1e-6):
            raise ValueError("Weights must be between 0 and 1 and sum to 1.")

        max_comments = 0
        max_views = 0

        for post_id, post in self.posts.items():
            num_comments = post.get_num_comments()
            num_views = post.get_num_views()
            if num_comments > max_comments:
                max_comments = num_comments
            if num_views > max_views:
                max_views = num_views

        norm_max_comments = max_comments if max_comments > 0 else 1
        norm_max_views = max_views if max_views > 0 else 1

        for post_id, post in self.posts.items():
            normalized_comments = post.get_num_comments() / norm_max_comments
            normalized_views = post.get_num_views() / norm_max_views
            importance = (comment_weight * normalized_comments) + (view_weight * normalized_views)
            self.graph.nodes[post_id]['importance'] = importance
        print(f"Calculated importance for posts using comment_weight={comment_weight}, view_weight={view_weight}")


    def create_diagram(self, comment_weight=0.5, view_weight=0.5, layout_algorithm=nx.spring_layout,
                       dimensions='2d', num_important_posts_to_highlight=5, show_labels=True):
        """
        Produces a 2D or 3D diagram of the social media data.
        Highlights the most important posts based on the chosen criteria.

        Args:
            comment_weight (float): Weight for comments in importance calculation (0 to 1).
            view_weight (float): Weight for views in importance calculation (0 to 1).
            layout_algorithm: NetworkX layout function (e.g., nx.spring_layout, nx.circular_layout).
            dimensions (str): '2d' or '3d'.
            num_important_posts_to_highlight (int): Number of top posts to visibly highlight.
            show_labels (bool): Whether to show node labels.
        """
        self._calculate_post_importance(comment_weight, view_weight)

        node_sizes = []
        node_colors = []
        node_labels = {}
        post_importance_scores = {}

        for node, data in self.graph.nodes(data=True):
            if data['type'] == 'post':
                post_importance_scores[node] = data['importance']

        sorted_posts_by_importance = sorted(post_importance_scores.items(), key=lambda item: item[1], reverse=True)
        highlight_threshold = sorted_posts_by_importance[min(num_important_posts_to_highlight, len(sorted_posts_by_importance)) - 1][1] if sorted_posts_by_importance else 0

        for node, data in self.graph.nodes(data=True):
            if data['type'] == 'user':
                node_sizes.append(100)
                node_colors.append('skyblue')
                node_labels[node] = node
            elif data['type'] == 'post':
                importance = data.get('importance', 0)
                size = 50 + importance * 300
                node_sizes.append(size)

                if importance >= highlight_threshold and num_important_posts_to_highlight > 0:
                    node_colors.append('red')
                else:
                    node_colors.append('lightcoral')
                node_labels[node] = node

        pos = layout_algorithm(self.graph, seed=42)

        fig = plt.figure(figsize=(12, 10))

        if dimensions == '2d':
            ax = fig.add_subplot(111)
            nx.draw_networkx_nodes(self.graph, pos, node_size=node_sizes, node_color=node_colors, ax=ax)
            nx.draw_networkx_edges(self.graph, pos, edgelist=[(u, v) for u, v, d in self.graph.edges(data=True) if d['relation'] != 'commented_on'],
                                   arrowsize=10, ax=ax, alpha=0.5)
            if show_labels:
                nx.draw_networkx_labels(self.graph, pos, labels=node_labels, font_size=8, ax=ax)
            ax.set_title(f'Social Network Diagram (2D) - Importance: Comments={comment_weight}, Views={view_weight}')
            ax.set_facecolor('lightgray')
            plt.axis('off')

        elif dimensions == '3d':
            from mpl_toolkits.mplot3d import Axes3D
            ax = fig.add_subplot(111, projection='3d')

            if all(len(p) == 3 for p in pos.values()):
                node_xyz = [(pos[v][0], pos[v][1], pos[v][2]) for v in self.graph.nodes()]
            else:
                node_xyz = [(pos[v][0], pos[v][1], 0) for v in self.graph.nodes()]

            x_coords, y_coords, z_coords = zip(*node_xyz)

            ax.scatter(x_coords, y_coords, z_coords, s=node_sizes, c=node_colors, alpha=0.8, edgecolors='w')

            for edge in self.graph.edges():
                x = [pos[edge[0]][0], pos[edge[1]][0]]
                y = [pos[edge[0]][1], pos[edge[1]][1]]
                z = [pos[edge[0]][2] if len(pos[edge[0]]) == 3 else 0,
                     pos[edge[1]][2] if len(pos[edge[1]]) == 3 else 0]
                ax.plot(x, y, z, c='gray', alpha=0.5, linewidth=0.8)

            if show_labels:
                for node, (x, y, z) in zip(self.graph.nodes(), node_xyz):
                    ax.text(x, y, z, s=node_labels[node], size=8, zorder=1, color='k')

            ax.set_title(f'Social Network Diagram (3D) - Importance: Comments={comment_weight}, Views={view_weight}')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_facecolor('lightgray')
            ax.grid(False)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            max_range = max(max(x_coords) - min(x_coords), max(y_coords) - min(y_coords), max(z_coords) - min(z_coords))
            mid_x = (max(x_coords) + min(x_coords)) * 0.5
            mid_y = (max(y_coords) + min(y_coords)) * 0.5
            mid_z = (max(z_coords) + min(z_coords)) * 0.5
            ax.set_xlim(mid_x - max_range / 2, mid_x + max_range / 2)
            ax.set_ylim(mid_y - max_range / 2, mid_y + max_range / 2)
            ax.set_zlim(mid_z - max_range / 2, mid_z + max_range / 2)

        else:
            raise ValueError("Dimensions must be '2d' or '3d'.")

        plt.show()

    def _get_filtered_posts(self, include_keywords=None, exclude_keywords=None,
                            user_attribute_filters=None, post_time_range=None):
        """
        Filters posts based on keywords, user attributes, and time range.
        Returns a list of Post objects that match the criteria.
        """
        filtered_posts = []

        include_keywords = [k.lower() for k in include_keywords] if include_keywords else []
        exclude_keywords = [k.lower() for k in exclude_keywords] if exclude_keywords else []
        user_attribute_filters = user_attribute_filters if user_attribute_filters is not None else {}

        for post_id, post in self.posts.items():
            if post_time_range:
                start_time, end_time = post_time_range
                if not (start_time <= post.creation_time <= end_time):
                    continue

            user_match = True
            for attr_key, attr_value in user_attribute_filters.items():
                if attr_key not in post.author.attributes or post.author.attributes[attr_key] != attr_value:
                    user_match = False
                    break
            if not user_match:
                continue

            post_content_lower = post.content.lower()

            if include_keywords:
                found_include_keyword = False
                for keyword in include_keywords:
                    if keyword in post_content_lower:
                        found_include_keyword = True
                        break
                if not found_include_keyword:
                    continue
            
            found_exclude_keyword = False
            for keyword in exclude_keywords:
                if keyword in post_content_lower:
                    found_exclude_keyword = True
                    break
            if found_exclude_keyword:
                continue

            filtered_posts.append(post)

        return filtered_posts

    def generate_word_cloud(self, include_keywords=None, exclude_keywords=None,
                            user_attribute_filters=None, post_time_range=None,
                            max_words=200, stopwords=None, background_color='white'):
        print("Generating word cloud...")
        filtered_posts = self._get_filtered_posts(
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
            user_attribute_filters=user_attribute_filters,
            post_time_range=post_time_range
        )

        if not filtered_posts:
            print("No posts matched the filtering criteria. Cannot generate word cloud.")
            return

        all_text = " ".join([post.content for post in filtered_posts])

        words = re.findall(r'\b\w+\b', all_text.lower())

        final_stopwords = set(STOPWORDS)
        if stopwords:
            final_stopwords.update(word.lower() for word in stopwords)

        meaningful_words = [word for word in words if word not in final_stopwords and len(word) > 1]

        word_counts = Counter(meaningful_words)

        wordcloud = WordCloud(width=800, height=400,
                              background_color=background_color,
                              max_words=max_words,
                              stopwords=final_stopwords,
                              min_font_size=10).generate_from_frequencies(word_counts)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        filter_summary = []
        if include_keywords: filter_summary.append(f"Inc. Keywords: {', '.join(include_keywords)}")
        if exclude_keywords: filter_summary.append(f"Exc. Keywords: {', '.join(exclude_keywords)}")
        if user_attribute_filters: filter_summary.append(f"User Attrs: {user_attribute_filters}")
        if post_time_range: filter_summary.append(f"Time: {post_time_range[0].strftime('%Y-%m-%d')} to {post_time_range[1].strftime('%Y-%m-%d')}")
        
        title = "Word Cloud"
        if filter_summary:
            title += f" ({'; '.join(filter_summary)})"
        plt.title(title)
        plt.show()