<script>
  import { onMount, createEventDispatcher } from "svelte";
  
  const dispatch = createEventDispatcher();

  export let disabled = [];
  export let faces = [];

  onMount(async () => {
    disabled = faces.map((f) => f.id);
  });

  const onFaceSelected = (face) => {
    touch();
    if (disabled.includes(face.id)) {
      disabled = disabled.filter((s) => s !== face.id);
    } else {
      disabled = [...disabled, face.id];
    }
  };
  const touch = () => dispatch('touch');
</script>

<div class="face-picker p-logo-section">
  <div class="p-logo-section__items">
    {#each faces as face}
      <div class="p-logo-section__item">
        <img
          class="face"
          src={face.url}
          alt={"face " + face.id}
          class:disabled={disabled.includes(face.id)}
          on:click={() => onFaceSelected(face)}
        />
      </div>
    {/each}
  </div>
</div>

<style lang="scss">
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
