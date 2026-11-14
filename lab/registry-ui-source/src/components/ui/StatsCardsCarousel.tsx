"use client";

import {
    useCallback,
    useEffect,
    useLayoutEffect,
    useRef,
    useState,
    type ComponentType,
} from "react";
import Image from "next/image";

const VISIBLE_COUNT = 4;

interface StatsCardsCarouselProps<T extends string> {
    cards: T[];
    activeCard: T;
    onSelectCard: (card: T) => void;
    StatsCardComponent: ComponentType<{
        stats_endpoint: string;
        active?: boolean;
    }>;
    statsEndpointFor: (type: T) => string;
}

export default function StatsCardsCarousel<T extends string>({
    cards,
    activeCard,
    onSelectCard,
    StatsCardComponent,
    statsEndpointFor,
}: StatsCardsCarouselProps<T>) {
    const maxOffset = Math.max(0, cards.length - VISIBLE_COUNT);
    const [offset, setOffset] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);
    const viewportRef = useRef<HTMLDivElement>(null);
    const trackRef = useRef<HTMLDivElement>(null);
    const offsetRef = useRef(offset);
    const wheelLockRef = useRef(false);
    const [cardWidth, setCardWidth] = useState(0);
    const [slideStep, setSlideStep] = useState(0);

    offsetRef.current = offset;

    const activeIndex = cards.indexOf(activeCard);

    const measureLayout = useCallback(() => {
        const viewport = viewportRef.current;
        const track = trackRef.current;
        if (!viewport || !track || cards.length === 0) return;

        const gap = parseFloat(getComputedStyle(track).columnGap || "0") || 0;
        const width =
            (viewport.clientWidth - gap * (VISIBLE_COUNT - 1)) / VISIBLE_COUNT;
        setCardWidth(width);
        setSlideStep(width + gap);
    }, [cards.length]);

    useLayoutEffect(() => {
        measureLayout();
    }, [measureLayout]);

    useEffect(() => {
        const viewport = viewportRef.current;
        if (!viewport) return;

        const observer = new ResizeObserver(() => measureLayout());
        observer.observe(viewport);
        return () => observer.disconnect();
    }, [measureLayout]);

    useEffect(() => {
        if (activeIndex < 0) return;
        setOffset((current) => {
            if (activeIndex < current) return activeIndex;
            if (activeIndex >= current + VISIBLE_COUNT) {
                return activeIndex - VISIBLE_COUNT + 1;
            }
            return current;
        });
    }, [activeIndex]);

    const canScrollBack = offset > 0;
    const canScrollForward = offset < maxOffset;

    const scrollBack = () => {
        setOffset((current) => Math.max(0, current - 1));
    };

    const scrollForward = () => {
        setOffset((current) => Math.min(maxOffset, current + 1));
    };

    useEffect(() => {
        const container = containerRef.current;
        if (!container || maxOffset === 0) return;

        const onWheel = (e: WheelEvent) => {
            const delta =
                Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
            if (delta === 0) return;

            e.preventDefault();
            e.stopPropagation();

            const currentOffset = offsetRef.current;
            const scrollingForward = delta > 0;
            const scrollingBack = delta < 0;

            if (scrollingForward && currentOffset >= maxOffset) return;
            if (scrollingBack && currentOffset <= 0) return;

            if (wheelLockRef.current) return;
            wheelLockRef.current = true;
            window.setTimeout(() => {
                wheelLockRef.current = false;
            }, 450);

            if (scrollingForward) {
                setOffset((current) => {
                    const next = Math.min(maxOffset, current + 1);
                    offsetRef.current = next;
                    return next;
                });
            } else {
                setOffset((current) => {
                    const next = Math.max(0, current - 1);
                    offsetRef.current = next;
                    return next;
                });
            }
        };

        container.addEventListener("wheel", onWheel, {
            passive: false,
            capture: true,
        });
        return () =>
            container.removeEventListener("wheel", onWheel, { capture: true });
    }, [maxOffset]);

    const arrowButtonClass =
        'relative z-10 shrink-0 self-center flex h-[30px] w-[30px] items-center justify-center rounded-[30px] bg-transparent cursor-pointer disabled:cursor-default';

    return (
        <div
            ref={containerRef}
            className="relative w-full flex items-stretch gap-2 overscroll-none"
        >
            <button
                type="button"
                disabled={!canScrollBack}
                onClick={(e) => {
                    e.stopPropagation();
                    if (canScrollBack) scrollBack();
                }}
                className={arrowButtonClass}
                aria-label="Show previous stats cards"
            >
                <Image
                    src="/images/common/black_arrow.png"
                    width={30}
                    height={30}
                    alt=""
                    className="rotate-180"
                />
            </button>

            <div
                ref={viewportRef}
                className="flex flex-1 min-w-0 overflow-hidden"
            >
                <div
                    ref={trackRef}
                    className="flex gap-4 sm:gap-5 lg:gap-6 will-change-transform motion-reduce:transition-none"
                    style={{
                        transform:
                            slideStep > 0
                                ? `translateX(-${offset * slideStep}px)`
                                : undefined,
                        transition:
                            'transform 500ms cubic-bezier(0.4, 0, 0.2, 1) 75ms',
                    }}
                >
                    {cards.map((type) => (
                        <div
                            key={type}
                            role="group"
                            tabIndex={0}
                            onKeyDown={e=>{if(e.target===e.currentTarget && (e.key==='Enter'||e.key===' ')){e.preventDefault();onSelectCard(type)}}}
                            onClick={() => onSelectCard(type)}
                            className="bg-transparent p-0 text-left shrink-0 min-w-0"
                            style={cardWidth > 0 ? { width: cardWidth } : undefined}
                        >
                            <StatsCardComponent
                                stats_endpoint={statsEndpointFor(type)}
                                active={activeCard === type}
                            />
                        </div>
                    ))}
                </div>
            </div>

            <button
                type="button"
                disabled={!canScrollForward}
                onClick={(e) => {
                    e.stopPropagation();
                    if (canScrollForward) scrollForward();
                }}
                className={arrowButtonClass}
                aria-label="Show more stats cards"
            >
                <Image
                    src="/images/common/black_arrow.png"
                    width={30}
                    height={30}
                    alt=""
                />
            </button>
        </div>
    );
}
