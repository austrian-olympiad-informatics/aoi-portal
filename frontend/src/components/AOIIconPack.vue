<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    role="img"
    aria-hidden
    :style="{
      'font-size': size,
      height: size,
      width: size,
    }"
  >
    <path :d="iconPath" />
  </svg>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import {
  mdiAccount,
  mdiAccountCircle,
  mdiAccountGroup,
  mdiAccountMultiple,
  mdiAccountPlus,
  mdiAlert,
  mdiAlertCircle,
  mdiAlertOctagon,
  mdiArrowDown,
  mdiArrowLeft,
  mdiArrowUp,
  mdiBriefcase,
  mdiCalendar,
  mdiCalendarToday,
  mdiCertificate,
  mdiCheck,
  mdiChevronDown,
  mdiChevronLeft,
  mdiChevronRight,
  mdiClockOutline,
  mdiClose,
  mdiCloseCircle,
  mdiCodeBraces,
  mdiCodeTags,
  mdiCog,
  mdiDelete,
  mdiDownload,
  mdiEarth,
  mdiEmail,
  mdiEmailNewsletter,
  mdiEye,
  mdiEyeOff,
  mdiFormatBold,
  mdiFormatItalic,
  mdiFormatListBulleted,
  mdiFormatListNumbered,
  mdiFormatQuoteClose,
  mdiFormatSize,
  mdiFormatStrikethrough,
  mdiFormatUnderline,
  mdiInformation,
  mdiLinkVariant,
  mdiLogin,
  mdiLogout,
  mdiMagnify,
  mdiMedal,
  mdiMemory,
  mdiMenuDown,
  mdiMenuUp,
  mdiMinus,
  mdiPencil,
  mdiPlus,
  mdiRedo,
  mdiRefresh,
  mdiReload,
  mdiTimerOutline,
  mdiUndo,
  mdiWeb,
} from "@mdi/js";

type IconLookupType = {
  [key: string]: string;
};

const ICON_LOOKUP: IconLookupType = {
  cog: mdiCog,
  "account-circle": mdiAccountCircle,
  alert: mdiAlert,
  "alert-circle": mdiAlertCircle,
  "chevron-left": mdiChevronLeft,
  "chevron-right": mdiChevronRight,
  "chevron-down": mdiChevronDown,
  "eye-off": mdiEyeOff,
  "menu-down": mdiMenuDown,
  "menu-up": mdiMenuUp,
  "close-circle": mdiCloseCircle,
  check: mdiCheck,
  information: mdiInformation,
  "arrow-up": mdiArrowUp,
  "arrow-down": mdiArrowDown,
  eye: mdiEye,
  account: mdiAccount,
  logout: mdiLogout,
  "calendar-today": mdiCalendarToday,
  medal: mdiMedal,
  "account-group": mdiAccountGroup,
  email: mdiEmail,
  "email-newsletter": mdiEmailNewsletter,
  magnify: mdiMagnify,
  "account-plus": mdiAccountPlus,
  pencil: mdiPencil,
  delete: mdiDelete,
  "account-multiple": mdiAccountMultiple,
  login: mdiLogin,
  refresh: mdiRefresh,
  close: mdiClose,
  plus: mdiPlus,
  "format-size": mdiFormatSize,
  "format-bold": mdiFormatBold,
  "format-underline": mdiFormatUnderline,
  "format-italic": mdiFormatItalic,
  "format-strikethrough": mdiFormatStrikethrough,
  "link-variant": mdiLinkVariant,
  "code-braces": mdiCodeBraces,
  "code-tags": mdiCodeTags,
  minus: mdiMinus,
  redo: mdiRedo,
  undo: mdiUndo,
  "format-quote-close": mdiFormatQuoteClose,
  "format-list-numbered": mdiFormatListNumbered,
  "format-list-bulleted": mdiFormatListBulleted,
  "timer-outline": mdiTimerOutline,
  memory: mdiMemory,
  "arrow-left": mdiArrowLeft,
  download: mdiDownload,
  earth: mdiEarth,
  briefcase: mdiBriefcase,
  certificate: mdiCertificate,
  calendar: mdiCalendar,
  reload: mdiReload,
  web: mdiWeb,
  "clock-outline": mdiClockOutline,
  "alert-octagon": mdiAlertOctagon,
};

@Component
export default class AOIIconPack extends Vue {
  @Prop({
    type: Array,
  })
  icon!: string[];

  @Prop({
    type: String,
  })
  size!: string;

  @Prop({
    type: String,
  })
  customClass!: string;

  mounted() {
    if (!(this.icon[1] in ICON_LOOKUP)) {
      console.warn(
        `Unknown icon ${this.icon[1]}, please add it to the list in src/components/AOIIconPack.vue`,
      );
    }
  }

  get iconPath() {
    return ICON_LOOKUP[this.icon[1]];
  }
}
</script>
