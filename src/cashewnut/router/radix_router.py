class RouterNode:
    def __init__(self, path, pipeline=()):
        self.path = path
        self.children = {}
        self.middlewares = list(pipeline)
        self.controllers = {
            "GET": None,
            "QUERY": None,
            "POST": None,
            "PUT": None,
            "PATCH": None,
            "DELETE": None,
        }


class RouterTree:
    def __init__(self):
        self.root = RouterNode("")

    def __insert(self, new_method: str, new_path: str, pipeline, controller=None):
        current_node = self.root
        path_segments = new_path.strip("/").split("/")

        for segment in path_segments:
            if segment not in current_node.children:
                current_node.children[segment] = RouterNode(segment, pipeline)
            current_node = current_node.children[segment]

        current_node.controllers[new_method] = controller
        return self

    def get_pipeline(self, method: str, path: str):
        current_node = self.root
        path_segments = path.strip("/").split("/")
        pipeline = []

        for segment in path_segments:
            if segment in current_node.children:
                current_node = current_node.children[segment]
                pipeline.append(current_node.middlewares)
            else:
                return None

        controller = current_node.controllers.get(method, None)
        if controller is None:
            return []
        return pipeline, controller

    def __str__(self, current_node=None, parent_path="", pipeline=[]):
        docs = []
        if current_node is None:
            current_node = self.root

        for child in current_node.children.values():
            for method, controller in child.controllers.items():
                if controller is not None:
                    doc = f"{method} {parent_path}/{child.path}"
                    for middleware in pipeline:
                        doc += f" -> {middleware.__name__}"
                    doc += f" -> {controller.__name__}"
                    docs.append(doc)
            child_docs = self.__str__(
                child, parent_path + "/" + child.path, pipeline + child.middlewares
            )
            if child_docs:
                docs.append(child_docs)

        return "\n".join(docs)

    def post(self, path: str, *pipeline, controller=None):
        return self.__insert("POST", path, pipeline, controller)

    def get(self, path: str, *pipeline, controller):
        return self.__insert("GET", path, pipeline, controller)

    def query(self, path: str, *pipeline, controller):
        return self.__insert("QUERY", path, pipeline, controller)

    def patch(self, path: str, *pipeline, controller):
        return self.__insert("PATCH", path, pipeline, controller)

    def put(self, path: str, *pipeline, controller):
        return self.__insert("PUT", path, pipeline, controller)

    def delete(self, path: str, *pipeline, controller):
        return self.__insert("DELETE", path, pipeline, controller)

    def use(self, path: str, *pipeline):
        return self.__insert("USE", path, pipeline)


if __name__ == "__main__":

    def test_middleware_1():
        return "Middleware 1"

    def test_middleware_2():
        return "Middleware 2"

    def test_middleware_3():
        return "Middleware 3"

    def test_controller_1():
        return "Test Controller 1"

    router = RouterTree()
    router.use("/v1", test_middleware_3)
    router.query("/v1/users", test_middleware_1, controller=test_controller_1)
    router.post("/v1/users/:id", test_middleware_2, controller=test_controller_1)
    router.post(
        "/v1/posts/:id",
        test_middleware_1,
        test_middleware_2,
        controller=test_controller_1,
    )
    print(router)
