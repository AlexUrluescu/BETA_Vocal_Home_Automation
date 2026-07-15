class AppFlow {
  constructor() {
    this.url = process.env.REACT_APP_SERVER_URL;
  }

  fetchStatus = async () => {
    try {
      const res = await fetch(`${this.url}/status`);
      const data = await res.json();

      return data[0];
    } catch (error) {
      console.log(error);
    }
  };

  fetchTreshold = async () => {
    try {
      const res = await fetch(`${this.url}/treshold`);
      const data = await res.json();
      const treshold = data[0].temperature;

      return treshold;
    } catch (error) {
      console.log(error);
    }
  };

  updateStatus = async (id, status) => {
    try {
      const data = await fetch(`${this.url}/update-status/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status }),
      });

      const res = await data.json();

      if (res.message === "On") {
        const status = 1;
        return status;
      } else {
        const status = 0;
        return status;
      }
    } catch (error) {
      console.log(error);
    }
  };
}

const appFlow = new AppFlow();

export { appFlow as AppFlow };
