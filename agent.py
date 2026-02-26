from kubernetes import client, config, watch
import redis
import os
from google import genai


def load_k8s_config():
    """
    Loads K8S cluster configuration.
    Tries to load in-cluster config first (for production/pod),
    and falls back to local kubeconfig (for local development).
    """
    try:
        config.load_incluster_config()
        print("Loaded in-cluster K8S configuration.")
    except config.config_exception.ConfigException:
        config.load_kube_config()
        print("Loaded local K8S configuration.")


def analyze_with_ai(pod_name, reason, message, logs):
    """
    Sends the Kubernetes error context and logs to Gemini AI using the NEW SDK.
    """
    print("🧠 Sending data to Gemini AI for analysis...")
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "❌ Error: GEMINI_API_KEY environment variable is missing."

        # Initialize the new client from google.genai
        client = genai.Client(api_key=api_key)

        prompt = f"""
        You are an expert DevOps engineer. Analyze the following Kubernetes Pod failure and provide a short, concise explanation of the root cause and a clear recommendation on how to fix it.

        Pod Name: {pod_name}
        Failure Reason: {reason}
        Kubernetes Message: {message}

        Pod Logs (last 50 lines):
        {logs}
        """

        # Call the API using the new syntax with the current free-tier model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ Failed to get AI analysis: {str(e)}"

def main():
    # 1. Initialize Kubernetes API client
    load_k8s_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    # 2. Initialize Redis connection
    # Note: Using 'localhost' for local script execution with port-forward.
    # Change to 'my-redis-master-0' when deploying inside the cluster.
    try:
        r = redis.Redis(host='my-redis-master', port=6379, decode_responses=True)
        r.ping()
        print("Connected to Redis successfully!")
    except redis.ConnectionError:
        print("Could not connect to Redis. Make sure port-forward is running.")
        return

    print("Starting to watch for pod events...")

    # 3. Fetch the current cluster state to avoid processing historical events
    initial_events = v1.list_event_for_all_namespaces()
    current_resource_version = initial_events.metadata.resource_version

    # 4. Stream new events starting from the current resource version
    for event in w.stream(v1.list_event_for_all_namespaces, resource_version=current_resource_version):
        obj = event['object']

        # 5. Filter out normal events, focus only on warnings/errors
        if obj.type == 'Warning':
            kind = obj.involved_object.kind
            name = obj.involved_object.name
            namespace = obj.involved_object.namespace
            reason = obj.reason
            message = obj.message

            # 6. Deduplication mechanism using Redis Cache
            if r.exists(name):
                # Skip this event if we recently alerted about this specific pod
                continue

                # Save the pod name in Redis with a Time-To-Live (TTL) of 300 seconds
            r.setex(name, 300, "alerted")

            print(f"\n🚨 ALERT DETECTED: {kind} {name} in namespace {namespace}")
            print(f"Reason: {reason} | Message: {message}")

            # 7. Fetch logs for crashing pods to provide context
            if kind == 'Pod':
                print(f"Fetching logs for Pod {name}...")
                logs = None

                try:
                    # Attempt 1: Try getting the current container's logs
                    logs = v1.read_namespaced_pod_log(
                        name=name,
                        namespace=namespace,
                        tail_lines=50
                    )
                except client.exceptions.ApiException as e:
                    print(f"Current logs not available: {e.reason}. Trying previous container...")

                # Attempt 2: If empty or failed, try fetching the 'previous' crashed container
                if not logs:
                    try:
                        logs = v1.read_namespaced_pod_log(
                            name=name,
                            namespace=namespace,
                            tail_lines=50,
                            previous=True
                        )
                    except client.exceptions.ApiException as e:
                        print(f"Could not fetch previous logs either: {e.reason}")

                # 8. Output the final logs and send to AI
                if logs:
                    print("--- Pod Logs Retrieved ---")

                    # Call the AI function with the gathered K8s data
                    ai_analysis = analyze_with_ai(name, reason, message, logs)

                    # Print the AI's root cause analysis to the console
                    print("\n🤖 === AI ROOT CAUSE ANALYSIS ===")
                    print(ai_analysis)
                    print("==================================\n")
                else:
                    print("--- No logs found for this Pod (It may not have started) ---")


if __name__ == "__main__":
    main()