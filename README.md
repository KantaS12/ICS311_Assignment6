# Result

=== Test 1: Basic Functionality ===
Users: 3
Posts: 3
Graph nodes: 6
Graph edges: 12
Calculated importance for posts using comment_weight=0.7, view_weight=0.3
post1: 2 comments, 2 views, importance: 1.000
post2: 1 comments, 2 views, importance: 0.650
post3: 0 comments, 2 views, importance: 0.300

=== Test 2: Word Cloud Filters ===
=== Test 1: Basic Functionality ===
Users: 3
Posts: 3
Graph nodes: 6
Graph edges: 12
Calculated importance for posts using comment_weight=0.7, view_weight=0.3
post1: 2 comments, 2 views, importance: 1.000
post2: 1 comments, 2 views, importance: 0.650
post3: 0 comments, 2 views, importance: 0.300

--- Word cloud with no filters ---
Generating word cloud...

--- Word cloud including 'technology' or 'AI' ---
Generating word cloud...

--- Word cloud excluding 'weather' ---
Generating word cloud...

--- Word cloud from NYC users only ---
Generating word cloud...

--- Word cloud from posts after Jan 2nd ---
Generating word cloud...

=== Test 3: Network Visualization ===
=== Test 1: Basic Functionality ===
Users: 3
Posts: 3
Graph nodes: 6
Graph edges: 12
Calculated importance for posts using comment_weight=0.7, view_weight=0.3
post1: 2 comments, 2 views, importance: 1.000
post2: 1 comments, 2 views, importance: 0.650
post3: 0 comments, 2 views, importance: 0.300
Creating 2D network diagram...
Calculated importance for posts using comment_weight=0.6, view_weight=0.4
Creating 3D network diagram...
Calculated importance for posts using comment_weight=0.8, view_weight=0.2

=== Test 4: Edge Cases ===
--- Testing with no posts ---
Generating word cloud...
No posts matched the filtering criteria. Cannot generate word cloud.
--- Testing invalid weights ---
=== Test 1: Basic Functionality ===
Users: 3
Posts: 3
Graph nodes: 6
Graph edges: 12
Calculated importance for posts using comment_weight=0.7, view_weight=0.3
post1: 2 comments, 2 views, importance: 1.000
post2: 1 comments, 2 views, importance: 0.650
post3: 0 comments, 2 views, importance: 0.300
Correctly caught error: Weights must be between 0 and 1 and sum to 1.
--- Testing posts with no engagement ---
Calculated importance for posts using comment_weight=0.5, view_weight=0.5
Post with no engagement has importance: 0.0

=== Test 5: Complex Scenario ===
Complex scenario: 5 users, 8 posts
Graph has 13 nodes and 22 edges
Generating word cloud...
Calculated importance for posts using comment_weight=0.9, view_weight=0.1

=== All Tests Completed ===
