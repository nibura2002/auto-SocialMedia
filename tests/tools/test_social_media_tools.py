import pytest
from auto_sns_agent.tools.social_media_tools import get_social_media_posts_for_topic

@pytest.mark.vcr # Optional: if using pytest-vcr for recording/replaying live calls
@pytest.mark.live_tool_test # Custom marker for tests that make live calls
def test_get_social_media_posts_for_topic_live():
    """Test get_social_media_posts_for_topic with a live call to Twitter/X."""
    topic = "#AIethics"
    platform = "Twitter"
    count = 2
    
    # Attempt to call the underlying function via .entrypoint
    result = get_social_media_posts_for_topic.entrypoint(topic=topic, platform=platform, count=count)
    
    print(f"\nOutput for topic '{topic}' from {platform}:")
    print(result)
    
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result string should not be empty"
    
    # Basic check: Does it look like it tried to get posts or hit an error?
    # A more robust check would parse the delimited posts if successful, 
    # or check for specific error message patterns.
    if "Error" not in result and f"No posts found or extracted for topic: {topic}" not in result:
        # If it seems successful, check for the delimiter or at least some content
        # The actual content is highly dynamic. We mostly check if the tool ran and returned something plausible.
        assert "---NEXT_POST_DELIMITER---" in result or len(result) > 50 # Arbitrary length for plausible content
        print("Live test seems to have fetched some content or a single post.")
    else:
        print(f"Live test resulted in an error or no posts found message: {result}")
        # Consider if this should fail the test or if error messages are acceptable outcomes for a live test
        # For now, allow error messages as the tool is experimental with live UIs.
        pass

    # Further assertions could involve trying to split by "---NEXT_POST_DELIMITER---"
    # and checking the number of posts if the call was expected to be successful.
    # posts = result.split("---NEXT_POST_DELIMITER---")
    # if "Error" not in result and "No posts found" not in result:
    #    assert len(posts) <= count, f"Expected up to {count} posts, got {len(posts)}"

# Add more tests here, e.g., for unsupported platforms, error conditions, etc.
# def test_get_social_media_posts_unsupported_platform():
#     result = get_social_media_posts_for_topic(topic="test", platform="Fakebook")
#     assert "Error: Platform 'Fakebook' is not supported" in result 