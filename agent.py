from kubernetes import client, config, watch
import redis

def load_k8s_config():
    """
    Loads K8S cluster configuration from the default location.
    """
    try:
        config.load_incluster_config()
        print("Loaded in-cluster K8S configuration.")
    except config.config_exception.ConfigException:
        config.load_kube_config()
        print("Loaded local K8S configuration.")

def main():
    load_k8s_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    print("Starting to watch for pod events...")

    initial_events = v1.list_event_for_all_namespaces()
    current_resource_version = initial_events.metadata.resource_version
    for event in w.stream(v1.list_event_for_all_namespaces, resource_version=current_resource_version):
        obj = event['object']

        if obj.type == 'Warning':
            kind = obj.involved_object.kind
            name = obj.involved_object.name

            namespace = obj.involved_object.namespace
            reason = obj.reason
            message = obj.message

            print(f"\n🚨 ALERT DETECTED: {kind} {name} in namespace {namespace}")
            print(f"Reason: {reason} | Message: {message}")

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

                # Print the results
                if logs:
                    print("--- Pod Logs Retrieved ---")
                    print(logs[:300] + "...\n" if len(logs) > 300 else logs)
                else:
                    print("--- No logs found for this Pod (It may not have started) ---")

if __name__ == "__main__":
    main()