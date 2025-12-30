interface WizardSourceInfo {
  name: string
  path: string
  size: number
  size_formatted: string
}

export const useCopyWizard = () => {
  const step = useState('wizardStep', () => 1) // 1=source, 2=dest, 3=summary
  const sourcePath = useState<string>('wizardSource', () => '')
  const destPath = useState<string>('wizardDest', () => '')
  const sourceInfo = useState<WizardSourceInfo | null>('wizardSourceInfo', () => null)
  const sourceItems = useState<WizardSourceInfo[]>('wizardSourceItems', () => [])

  const nextStep = () => {
    if (step.value < 3) {
      step.value++
    }
  }

  const prevStep = () => {
    if (step.value > 1) {
      step.value--
    }
  }

  const goToStep = (targetStep: number) => {
    if (targetStep >= 1 && targetStep <= 3) {
      step.value = targetStep
    }
  }

  const reset = () => {
    step.value = 1
    sourcePath.value = ''
    destPath.value = ''
    sourceInfo.value = null
    sourceItems.value = []
  }

  const setSource = (path: string | string[], info?: WizardSourceInfo | WizardSourceInfo[]) => {
    if (Array.isArray(path)) {
      sourcePath.value = path.length > 0 ? path[0] : ''
      sourceItems.value = Array.isArray(info) ? info : []
    } else {
      sourcePath.value = path
      if (info && !Array.isArray(info)) {
        sourceInfo.value = info
        sourceItems.value = [info]
      }
    }
  }

  const setDestination = (path: string) => {
    destPath.value = path
  }

  const isBulk = computed(() => sourceItems.value.length > 1)

  return {
    step,
    sourcePath,
    destPath,
    sourceInfo,
    sourceItems,
    isBulk,
    nextStep,
    prevStep,
    goToStep,
    reset,
    setSource,
    setDestination
  }
}

