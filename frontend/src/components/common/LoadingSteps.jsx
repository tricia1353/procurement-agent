import { Loader2 } from 'lucide-react'

export function LoadingSteps({ steps, currentStep }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-6" />
      <div className="space-y-2 w-full max-w-md">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
              index < currentStep
                ? 'bg-green-50 text-green-700'
                : index === currentStep
                ? 'bg-blue-50 text-blue-700'
                : 'bg-gray-50 text-gray-400'
            }`}
          >
            <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
              index < currentStep
                ? 'bg-green-500'
                : index === currentStep
                ? 'bg-blue-500 animate-pulse'
                : 'bg-gray-300'
            }`}>
              {index < currentStep ? (
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <span className="text-xs font-medium text-white">{index + 1}</span>
              )}
            </div>
            <span className="text-sm font-medium">{step}</span>
          </div>
        ))}
      </div>
    </div>
  )
}