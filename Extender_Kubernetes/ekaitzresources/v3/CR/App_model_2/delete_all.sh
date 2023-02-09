kubectl delete crd applications.ehu.gcis.org components.ehu.gcis.org

kubectl delete cm cm-data-processing-assemblystation
kubectl delete deploy data-processing-assemblystation

kubectl delete deploy data-processing-1-exist-data-processing-app-1-model-2
kubectl delete deploy data-processing-1-influx-data-processing-app-1-model-2
kubectl delete deploy data-processing-2-exist-data-processing-app-2-model-2
kubectl delete deploy data-processing-2-influx-data-processing-app-2-model-2

kubectl delete deploy data-acquisition-1-source-mqtt-kafka-data-acquisition-app-1-model-2
kubectl delete deploy data-acquisition-1-sink-exist-data-acquisition-app-1-model-2
kubectl delete deploy data-acquisition-2-source-mqtt-kafka-data-acquisition-app-2-model-2
kubectl delete deploy data-acquisition-2-sink-exist-data-acquisition-app-2-model-2



