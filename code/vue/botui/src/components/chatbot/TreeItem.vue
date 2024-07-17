<template>
  <ul class="tree-item">
    <li v-for="(value, key) in item" :key="key">
      <div
        v-if="typeof value === 'object'"
        @click="toggle"
        class="folder"
        :class="{ 'folder-open': isOpen }"
      >
        {{ key }}
      </div>
      <div
        v-else
        @click="$emit('select-file', value)"
        class="file"
      >
        {{ key }}
      </div>
      <TreeItem
        v-if="typeof value === 'object' && isOpen"
        :item="value"
        @select-file="$emit('select-file', $event)"
        class="nested"
        :expand-to-first-leaf="expandToFirstLeaf"
        :is-expanded="isOpen"
      />
    </li>
  </ul>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'TreeItem',
  props: {
    item: {
      type: Object,
      required: true
    },
    expandToFirstLeaf: {
      type: Boolean,
      default: false
    },
    isExpanded: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    const isOpen = ref(props.isExpanded)

    const toggle = () => {
      isOpen.value = !isOpen.value
    }

    const expandToFirstLeafNode = () => {
      if (props.expandToFirstLeaf) {
        const keys = Object.keys(props.item)
        if (keys.length > 0) {
          const firstValue = props.item[keys[0]]
          if (typeof firstValue === 'object') {
            isOpen.value = true
          } else {
            emit('select-file', firstValue)
          }
        }
      }
    }

    watch(() => props.expandToFirstLeaf, (newValue) => {
      if (newValue) {
        expandToFirstLeafNode()
      }
    }, { immediate: true })

    watch(() => props.isExpanded, (newValue) => {
      isOpen.value = newValue
    })

    return {
      isOpen,
      toggle
    }
  }
}
</script>

<style scoped>
.tree-item {
  list-style-type: none;
  padding-left: 20px;
}

.folder, .file {
  cursor: pointer;
  user-select: none;
  color: black; /* Change text color to black */
}

.folder::before {
  content: '▶';
  display: inline-block;
  margin-right: 6px;
  transition: transform 0.2s;
  color: #3490dc; /* Keep the arrow icon color blue */
}

.folder-open::before {
  transform: rotate(90deg);
}

.file:hover, .folder:hover {
  text-decoration: underline;
}

.nested {
  padding-left: 20px;
}
</style>