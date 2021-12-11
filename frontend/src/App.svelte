<script>
  import { Plane } from "svelte-loading-spinners";

  import Slider from "@bulatdashiev/svelte-slider";

  import { Observable } from "rxjs";
  // import FacePicker from "./FacePicker.svelte";

  const restore_backend_url = "http://localhost:8081"; // TODO remove -dev
  // const colorize_backend_url = "/api";
  const colorize_backend_url = "http://localhost:8080"; // TODO remove -dev

  const headers = {
    origin: "Original",
    v1: "Colourised V1",
    v2: "Colourised V2",
    restored: "Restored",
    faces: "Face picker",
  };

  const versions_bw = ["origin", "v1", "v2"];
  const versions_restore = ["origin", "restored", "faces"];

  let versions = versions_bw;
  let data = undefined;
  // let selectedFaces;

  const setImage = (version, blob) => {
    let reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onload = (e) => (data[version].image = e.target.result);
  };

  // data = JSON.parse(localStorage.getItem("data")); // TODO: remove -dev

  const onRestoreFaces = async (hash) => {
    data = { ...data, restored: { hash }, faces: {} };
    // // TODO: remove -dev
    // data["v1"].image = undefined;
    // data["v2"].image = undefined;
    // localStorage.setItem("data", JSON.stringify(data));
    // return
    versions = versions_restore;
    new Observable((subscriber) => {
      let poll;
      const requestRestoredPic = async () => {
        const response = await fetch(`${restore_backend_url}/restore/${hash}`);
        if (response.ok) {
          const response_data = await response.json();
          if (!!response_data.restored) {
            subscriber.next(response_data);
            return subscriber.complete();
          }
        }
        poll();
      };
      poll = () =>
        setTimeout(async () => {
          await requestRestoredPic();
        }, 3000);
      requestRestoredPic();
    }).subscribe((response) => {
      const base_path = `${restore_backend_url}/img/${response.hash}`;
      data.restored.image = `${base_path}${response.restored}`;
      data.faces.images = response.faces.map((face_url) => ({
        id: parseInt(face_url.split("/").reverse()[0].split(".")[0]),
        url: `${base_path}${face_url}`,
        disabled: true,
      }));
    });
  };

  const onFaceSelected = (face) => {
    face.disabled = !face.disabled;
    data.faces.touched = true;
    data.faces = { ...data.faces };
  };

  const onFaceRefresh = async () => {
    let body = new FormData();
    body.append("hash", data.restored.hash);
    body.append(
      "hide_faces",
      data.faces.images
        .filter((image) => image.disabled)
        .map((image) => image.id)
        .join(",")
    );
    fetch(`${restore_backend_url}/restore`, {
      method: "POST",
      body,
    }).then(() => onRestoreFaces(data.restored.hash));
  };

  const onFileSelected = async (e) => {
    // TODO: send to restore backend async
    let image = e.target.files[0];
    data = { v1: {}, v2: {}, origin: {} };
    versions = versions_bw;
    setImage("origin", image);

    let body = new FormData();
    body.append("image", image);

    const onReceiveColoredImg = (version) => async (result) => {
      if (result.ok) {
        const blob = await result.blob();
        setImage(version, blob);
        data[version].saturation = [100];
        data[version].hash = result.headers.get("x-image-hash");
        // TODO: original hash must be queried
      } else data[version].error = true;
    };

    const colorizeVersion = async (version) =>
      // TODO
      fetch(`${colorize_backend_url}/colorize?version=${version}`, {
        method: "POST",
        body,
      }).then(onReceiveColoredImg(version));

    colorizeVersion("v1");
    colorizeVersion("v2");
  };
</script>

<div class="l-site">
  <main class="l-main">
    <div class="row">
      <h1>Colourise!</h1>
    </div>

    <div class="row">
      <div class="col-12">
        <input
          type="file"
          accept=".jpg, .jpeg, .png"
          on:change={(e) => onFileSelected(e)}
        />
      </div>
    </div>

    {#if !data}
      <div class="row">
        <div class="col-12">
          <h3>Start by selecting a black and white picture.</h3>
        </div>
      </div>
    {:else}
      <div class="row">
        {#each versions as version}
          <div class="col-4">
            <!-- TODO: restored = goback -->
            <h2>
              {headers[version]}
              {#if version == "faces" && !!data.faces.touched}
                <button on:click={onFaceRefresh}>Apply</button>
                <!-- <i class="p-icon--success"></i> -->
              {/if}
            </h2>
          </div>
        {/each}
      </div>
      <div class="row images">
        {#each versions as version}
          <div class="col-4">
            {#if !!data[version].image}
              <img
                class="result"
                src={data[version].image}
                alt={version}
                style="filter: saturate({data[version].saturation ?? 100}%);"
              />
            {:else if !!data[version].images}
              <div class="p-logo-section">
                <div class="p-logo-section__items">
                  {#each data[version].images as face}
                    <div class="p-logo-section__item">
                      <img
                        src={face.url}
                        alt={"face " + face.id}
                        class={face.disabled ? "face disabled" : "face"}
                        on:click={() => onFaceSelected(face)}
                      />
                    </div>
                  {/each}
                </div>
              </div>
              <!-- <FacePicker bind:selected={selectedFaces} faces={data[version].images} /> -->
            {:else if !!data[version].error}
              <p>
                Error getting version {version}
              </p>
            {:else}
              <div class="loading">
                <Plane size="60" color="#FF3E00" unit="px" duration="1s" />
              </div>
            {/if}
          </div>
        {/each}
      </div>
      <div class="row">
        {#each versions as version}
          <div class="col-4 slider">
            {#if !!data[version].saturation}
              <Slider max="300" bind:value={data[version].saturation} />
            {/if}
            <!-- TODO: enable face restoration on colourised and original picture -->
            {#if !!data[version].hash}
              <button on:click={() => onRestoreFaces(data[version].hash)}>
                {data[version].hash}
              </button>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>

<style lang="scss">
  $color: #ff3e00;

  h1,
  h2 {
    color: $color;
    text-transform: uppercase;
  }

  h1 {
    font-size: 4em;
    font-weight: 100;
    margin-top: 24px;
  }

  input {
    padding: 32px;
    border: 2px dotted lightgray;
    margin: 8px;
  }

  .row {
    &.images {
      align-items: center;
    }
  }

  .loading {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  img {
    width: 100%;

    &.face {
      padding: 10px;
    }

    &.disabled {
      opacity: 0.5;
    }
  }

  .row div.slider {
    --thumb-bg: #d33601;
    --progress-bg: #ff3e00;
  }
</style>
