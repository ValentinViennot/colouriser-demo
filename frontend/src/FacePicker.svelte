<script>
  export let selected = [];
  export let faces = [];

  const onFaceSelected = (face) => {
    if (selected.includes(face.id)) {
      selected = selected.filter((s) => s !== face.id);
    } else {
      selected = [...selected, face.id];
    }
  };
</script>

<div class="face-picker p-logo-section">
  <div class="p-logo-section__items">
    {#each faces as face}
      <div class="p-logo-section__item">
        <img
          class="face"
          src={face.url}
          alt={"face " + face.id}
          class:disabled={!selected.includes(face.id)}
          on:click={() => onFaceSelected(face)}
        />
      </div>
    {/each}
  </div>
</div>

<style lang="scss">
  .face-picker {
    border: 1px solid red !important;
    background-color: lightcoral;
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
</style>
