.items[0] | "\(.metadata.annotations."alb.ingress.kubernetes.io/backend-protocol"|ascii_downcase )://\(.status.loadBalancer.ingress[0].hostname):\(.spec.rules[0].http.paths[0].backend.servicePort)"
