<template>
  <ul class="tree-item">
    <li v-for="(value, key) in item" :key="key">
      <div
        v-if="value.type === 'directory'"
        @click="toggle"
        class="folder"
        :class="{ 'folder-open': isOpen }"
      >
        {{ key }}
      </div>
      <div
        v-else-if="value.type === 'file'"
        @click="$emit('select-file', value.path)"
        class="file"
        :class="{ 'partial-file': value.is_partial }"
      >
        {{ key }}
      </div>
      <TreeItem
        v-if="value.type === 'directory' && isOpen"
        :item="value.children"
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
          if (firstValue.type === 'directory') {
            isOpen.value = true
          } else if (firstValue.type === 'file') {
            emit('select-file', firstValue.path)
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
  color: black;
}

.folder::before {
  content: '▶';
  display: inline-block;
  margin-right: 6px;
  transition: transform 0.2s;
  color: #3490dc;
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

.partial-file {
  color: #e74c3c;
}
</style>