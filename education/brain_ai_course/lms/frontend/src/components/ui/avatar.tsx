import * as React from "react"
import Image from "next/image"
import { cn, getInitials, generateAvatarColor } from "@/lib/utils"

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string | null
  alt?: string
  name?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  shape?: 'circle' | 'square'
}

const sizeClasses = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
  xl: 'h-16 w-16 text-xl',
}

const imageSizeMap = {
  xs: 24,
  sm: 32,
  md: 40,
  lg: 48,
  xl: 64,
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ 
    className, 
    src, 
    alt = "Avatar", 
    name,
    size = 'md',
    shape = 'circle',
    ...props 
  }, ref) => {
    const initials = name ? getInitials(name) : '?'
    const bgColor = name ? generateAvatarColor(name) : 'bg-slate-400'
    const borderRadius = shape === 'circle' ? 'rounded-full' : 'rounded-lg'
    
    return (
      <div
        ref={ref}
        className={cn(
          "relative flex shrink-0 overflow-hidden",
          sizeClasses[size],
          borderRadius,
          className
        )}
        {...props}
      >
        {src ? (
          <Image
            src={src}
            alt={alt}
            width={imageSizeMap[size]}
            height={imageSizeMap[size]}
            className={cn("aspect-square h-full w-full object-cover", borderRadius)}
          />
        ) : (
          <div
            className={cn(
              "flex h-full w-full items-center justify-center font-medium text-white",
              bgColor,
              borderRadius
            )}
          >
            {initials}
          </div>
        )}
      </div>
    )
  }
)
Avatar.displayName = "Avatar"

export interface AvatarGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  avatars: { src?: string | null; name?: string }[]
  max?: number
  size?: 'xs' | 'sm' | 'md' | 'lg'
}

const AvatarGroup = React.forwardRef<HTMLDivElement, AvatarGroupProps>(
  ({ 
    className, 
    avatars, 
    max = 5,
    size = 'sm',
    ...props 
  }, ref) => {
    const visibleAvatars = avatars.slice(0, max)
    const remainingCount = avatars.length - max
    
    const overlapClass = {
      xs: '-ml-2',
      sm: '-ml-2',
      md: '-ml-3',
      lg: '-ml-4',
    }

    return (
      <div
        ref={ref}
        className={cn("flex items-center", className)}
        {...props}
      >
        {visibleAvatars.map((avatar, index) => (
          <div
            key={index}
            className={cn(
              "relative ring-2 ring-white",
              index > 0 && overlapClass[size]
            )}
          >
            <Avatar
              src={avatar.src}
              name={avatar.name}
              size={size}
              alt={avatar.name || `Avatar ${index + 1}`}
            />
          </div>
        ))}
        {remainingCount > 0 && (
          <div
            className={cn(
              "relative flex items-center justify-center rounded-full bg-slate-200 text-slate-600 font-medium ring-2 ring-white",
              sizeClasses[size],
              overlapClass[size]
            )}
          >
            +{remainingCount}
          </div>
        )}
      </div>
    )
  }
)
AvatarGroup.displayName = "AvatarGroup"

export { Avatar, AvatarGroup }
