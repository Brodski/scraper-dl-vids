# Run the first command
 docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s

# Run the second command if the first failed
if (!$?) {
    echo "it failed 1"
    docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
    if (!$?) {
        echo "it failed 2"
        docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
        if (!$?) {
            echo "it failed 3"
            docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
            if (!$?) {
                echo "it failed 4"
                docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
                if (!$?) {
                    echo "it failed 5"
                    docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
                    if (!$?) {
                        echo "it failed 6"
                        docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
                        if (!$?) {
                            echo "it failed 7"
                            docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
                            if (!$?) {
                                echo "it failed 8"
                                docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2_prod_2024.10.28_30s
                            }
                        }
                    }
                }
            }
        }
    }
}
