import datetime
from socialMediaAnalysis import User, Post, Comment, SocialMediaAnalyzer

def test_basic_functionality():
    """Test basic user and post creation"""
    print("=== Test 1: Basic Functionality ===")
    
    # Create users
    alice = User("alice", {"age": 25, "location": "NYC"})
    bob = User("bob", {"age": 30, "location": "LA"})
    charlie = User("charlie", {"age": 22, "location": "NYC"})
    
    # Create posts
    post1 = Post("post1", alice, "Hello world! This is my first post about technology.", 
                 datetime.datetime(2024, 1, 1, 10, 0))
    post2 = Post("post2", bob, "Love this sunny weather in LA! Perfect for hiking.", 
                 datetime.datetime(2024, 1, 2, 14, 30))
    post3 = Post("post3", charlie, "Just finished reading an amazing book about AI and machine learning.", 
                 datetime.datetime(2024, 1, 3, 9, 15))
    
    # Add some views
    post1.add_viewer(bob, datetime.datetime(2024, 1, 1, 11, 0))
    post1.add_viewer(charlie, datetime.datetime(2024, 1, 1, 12, 0))
    post2.add_viewer(alice, datetime.datetime(2024, 1, 2, 15, 0))
    post2.add_viewer(charlie, datetime.datetime(2024, 1, 2, 16, 0))
    post3.add_viewer(alice, datetime.datetime(2024, 1, 3, 10, 0))
    post3.add_viewer(bob, datetime.datetime(2024, 1, 3, 11, 0))
    
    # Create comments
    comment1 = Comment("c1", bob, post1, "Great first post!", datetime.datetime(2024, 1, 1, 11, 30))
    comment2 = Comment("c2", charlie, post1, "Welcome to the platform!", datetime.datetime(2024, 1, 1, 12, 30))
    comment3 = Comment("c3", alice, post2, "I wish I was in LA too!", datetime.datetime(2024, 1, 2, 15, 30))
    
    # Add comments to posts
    post1.add_comment(comment1)
    post1.add_comment(comment2)
    post2.add_comment(comment3)
    
    # Add connections
    alice.add_connection(bob, "friend")
    bob.add_connection(alice, "friend")
    alice.add_connection(charlie, "colleague")
    
    users = [alice, bob, charlie]
    posts = [post1, post2, post3]
    
    analyzer = SocialMediaAnalyzer(users, posts)
    
    print(f"Users: {len(analyzer.users)}")
    print(f"Posts: {len(analyzer.posts)}")
    print(f"Graph nodes: {analyzer.graph.number_of_nodes()}")
    print(f"Graph edges: {analyzer.graph.number_of_edges()}")
    
    # Test post importance calculation
    analyzer._calculate_post_importance(comment_weight=0.7, view_weight=0.3)
    for post_id in analyzer.posts:
        importance = analyzer.graph.nodes[post_id].get('importance', 0)
        print(f"{post_id}: {analyzer.posts[post_id].get_num_comments()} comments, "
              f"{analyzer.posts[post_id].get_num_views()} views, importance: {importance:.3f}")
    
    return analyzer

def test_word_cloud_filters():
    """Test word cloud with different filters"""
    print("\n=== Test 2: Word Cloud Filters ===")
    
    # Create analyzer from previous test
    analyzer = test_basic_functionality()
    
    # Test 1: No filters
    print("\n--- Word cloud with no filters ---")
    analyzer.generate_word_cloud()
    
    # Test 2: Include keywords
    print("\n--- Word cloud including 'technology' or 'AI' ---")
    analyzer.generate_word_cloud(include_keywords=["technology", "AI"])
    
    # Test 3: Exclude keywords
    print("\n--- Word cloud excluding 'weather' ---")
    analyzer.generate_word_cloud(exclude_keywords=["weather"])
    
    # Test 4: User attribute filter
    print("\n--- Word cloud from NYC users only ---")
    analyzer.generate_word_cloud(user_attribute_filters={"location": "NYC"})
    
    # Test 5: Time range filter
    print("\n--- Word cloud from posts after Jan 2nd ---")
    analyzer.generate_word_cloud(
        post_time_range=(datetime.datetime(2024, 1, 2), datetime.datetime(2024, 12, 31))
    )

def test_network_visualization():
    """Test network diagram creation"""
    print("\n=== Test 3: Network Visualization ===")
    
    analyzer = test_basic_functionality()
    
    # Test different visualization parameters
    print("Creating 2D network diagram...")
    analyzer.create_diagram(
        comment_weight=0.6, 
        view_weight=0.4,
        num_important_posts_to_highlight=2,
        show_labels=True
    )
    
    print("Creating 3D network diagram...")
    analyzer.create_diagram(
        dimensions='3d',
        comment_weight=0.8, 
        view_weight=0.2,
        num_important_posts_to_highlight=1
    )

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Test 4: Edge Cases ===")
    
    # Test empty data
    print("--- Testing with no posts ---")
    alice = User("alice")
    analyzer_empty = SocialMediaAnalyzer([alice], [])
    analyzer_empty.generate_word_cloud()  # Should print "No posts matched"
    
    # Test invalid weight parameters
    print("--- Testing invalid weights ---")
    analyzer = test_basic_functionality()
    try:
        analyzer._calculate_post_importance(comment_weight=0.8, view_weight=0.8)  # Sum > 1
        print("ERROR: Should have raised ValueError")
    except ValueError as e:
        print(f"Correctly caught error: {e}")
    
    # Test posts with no comments or views
    print("--- Testing posts with no engagement ---")
    lonely_user = User("lonely")
    lonely_post = Post("lonely_post", lonely_user, "Nobody reads my posts", 
                       datetime.datetime(2024, 1, 4, 8, 0))
    
    analyzer_lonely = SocialMediaAnalyzer([lonely_user], [lonely_post])
    analyzer_lonely._calculate_post_importance()
    importance = analyzer_lonely.graph.nodes["lonely_post"].get('importance', 0)
    print(f"Post with no engagement has importance: {importance}")

def test_complex_scenario():
    """Test a more complex scenario with multiple interactions"""
    print("\n=== Test 5: Complex Scenario ===")
    
    # Create more users
    users = []
    for i in range(5):
        user = User(f"user{i}", {"age": 20 + i * 5, "department": f"dept{i % 3}"})
        users.append(user)
    
    # Create interconnected posts
    posts = []
    base_time = datetime.datetime(2024, 1, 1)
    
    for i in range(8):
        author = users[i % len(users)]
        post = Post(f"post_{i}", author, 
                    f"This is post number {i} about topic {i % 3}. Keywords: data science machine learning.",
                    base_time + datetime.timedelta(days=i))
        
        # Add random viewers and comments
        for j, viewer in enumerate(users):
            if viewer != author and (i + j) % 3 == 0:  # Some pattern for views
                post.add_viewer(viewer, base_time + datetime.timedelta(days=i, hours=j))
                
                if (i + j) % 5 == 0:  # Fewer comments than views
                    comment = Comment(f"c_{i}_{j}", viewer, post, f"Comment on post {i}",
                                      base_time + datetime.timedelta(days=i, hours=j + 1))
                    post.add_comment(comment)
        
        posts.append(post)
    
    # Add some connections between users
    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            if (i + j) % 2 == 0:
                users[i].add_connection(users[j], "colleague")
    
    analyzer = SocialMediaAnalyzer(users, posts)
    
    print(f"Complex scenario: {len(users)} users, {len(posts)} posts")
    print(f"Graph has {analyzer.graph.number_of_nodes()} nodes and {analyzer.graph.number_of_edges()} edges")
    
    # Test various filters
    analyzer.generate_word_cloud(
        include_keywords=["science", "learning"],
        user_attribute_filters={"department": "dept0"},
        max_words=50
    )
    
    analyzer.create_diagram(
        comment_weight=0.9,
        view_weight=0.1,
        num_important_posts_to_highlight=3
    )

if __name__ == "__main__":
    # Run all tests
    test_basic_functionality()
    test_word_cloud_filters() 
    test_network_visualization()
    test_edge_cases()
    test_complex_scenario()
    
    print("\n=== All Tests Completed ===")
