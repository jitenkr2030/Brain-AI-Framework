import * as React from "react"
import { cn } from "@/lib/utils"

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string
  label?: string
  options: { value: string | number; label: string }[]
  placeholder?: string
}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ 
    className, 
    error, 
    label, 
    options,
    placeholder = "Select an option",
    id,
    ...props 
  }, ref) => {
    const selectId = id || React.useId()
    
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={selectId}
            className="block text-sm font-medium text-slate-700 mb-1.5"
          >
            {label}
          </label>
        )}
        <div className="relative">
          <select
            id={selectId}
            className={cn(
              "flex h-10 w-full appearance-none rounded-lg border bg-white px-3 py-2 text-sm transition-colors",
              "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
              "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-slate-50",
              error
                ? "border-red-500 focus:ring-red-500"
                : "border-slate-300 hover:border-slate-400",
              className
            )}
            ref={ref}
            aria-invalid={error ? 'true' : 'false'}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    )
  }
)
Select.displayName = "Select"

export { Select }
